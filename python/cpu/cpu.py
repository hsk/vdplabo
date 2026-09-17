import pygame
# cpu.py
class CPU:
    def __init__(self):
        self.pc = 0x100
        self.acc = 0
        self.zero_flag = False
        self.irq_status = 0
        self.interrupt_enable = True
        self.interrupt_pending = False
        self.interrupt_vector = 0x10
        self.io = {}
        self.memory = {}
        self.stack = []
        self.running = True
    IRQ_VBLANK = 1
    IRQ_KEYBOARD = 2
    def find_label(self, label_name):
        for addr, inst in self.memory.items():
            if isinstance(inst,tuple) and inst[0] == "LABEL" and inst[1] == label_name:
                return addr + 1
        raise Exception(f"Label not found: {label_name}")
    def jmp(self, label, flg = True):
        if flg:
            self.pc = self.find_label(label) if isinstance(label, str) else label
    def io_read(self, addr):
        # IRQ status register
        if addr == 0x00:
            value = self.irq_status
            self.irq_status = 0
            return value
        return self.io.get(addr, 0)
    def io_write(self, addr, value):
        self.io[addr] = value
    def load_program(self, program, start=0):
        for i, inst in enumerate(program):
            self.memory[start + i] = inst
    def interrupt_request(self, irq_type):
        self.irq_status |= irq_type
        self.interrupt_pending = True
    def check_interrupt(self):
        if self.interrupt_enable and self.interrupt_pending:
            self.interrupt_pending = False
            # 現在PCを保存
            self.stack.append(self.pc)
            # 割り込み中はさらに割り込み禁止
            self.interrupt_enable = False
            # 割り込みハンドラへジャンプ
            self.pc = self.interrupt_vector
    def step(self):
        # 命令実行前に割り込みチェック
        self.check_interrupt()
        inst = self.memory.get(self.pc, ("NOP",))
        self.pc += 1
        match inst:
            case ("NOP",): pass
            case ("LABEL",): pass
            case ("LDI",v): self.acc = v
            case ("LDA",a): self.acc = self.memory.get(a, 0)
            case ("STA",a): self.memory[a] = self.acc
            case ("ADD",v): self.acc += v; self.zero_flag = (self.acc == 0)
            case ("SUB",v): self.acc -= v; self.zero_flag = (self.acc == 0)
            case ("AND",v): self.acc &= v; self.zero_flag = (self.acc == 0)
            case ("JMP",a): self.jmp(a)
            case ("JZ",a): self.jmp(a, self.zero_flag)
            case ("JNZ",a): self.jmp(a, not self.zero_flag)
            case ("IN",p): self.acc = self.io_read(p)
            case ("OUT",p): self.io_write(p, self.acc)
            case ("IRET",): self.pc = self.stack.pop(); self.interrupt_enable = True
            case ("POPA",): self.acc = self.stack.pop()
            case ("PUSHA",): self.stack.append(self.acc)
    def update(self):
        # CPU実行
        for _ in range(50):
            self.step()

class VDP:
    def __init__(self,cpu,w,h):
        self.cpu = cpu
        self.w = w
        self.h = h
        self.scale = 3
    def init(self):
        self.screen = pygame.display.set_mode((self.w * self.scale, self.h * self.scale))
    def update(self):
        # VBLANK IRQ
        self.cpu.interrupt_request(CPU.IRQ_VBLANK)
        self.screen.fill((0, 0, 0))
        x = self.cpu.memory.get(0x0e, 0)
        y = self.cpu.memory.get(0x0f, 0)
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (x * self.scale, y * self.scale, 16 * self.scale, 16 * self.scale)
        )
class Joy:
    def __init__(self, cpu):
        self.cpu = cpu
        self.state = 0xff
    def update(self):
        keys = pygame.key.get_pressed()
        state = 0
        if keys[pygame.K_LEFT]: state |= 0x1
        if keys[pygame.K_RIGHT]: state |= 0x2
        if keys[pygame.K_UP]: state |= 0x4
        if keys[pygame.K_DOWN]: state |= 0x8
        # キーボードIOへ反映
        self.cpu.io[0x10] = state
        # キーボードIRQ
        if state != self.state:
            self.cpu.interrupt_request(CPU.IRQ_KEYBOARD)
            self.state = state

def main(main_program, interrupt_handler):
    cpu = CPU()
    cpu.load_program(main_program, 0x0100)
    cpu.load_program(interrupt_handler, 0x10)
    pygame.init()
    vdp = VDP(cpu,256,192)
    vdp.init()
    joy = Joy(cpu)
    clock = pygame.time.Clock()
    running = True
    # 実行
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        joy.update()
        cpu.update()
        vdp.update()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

main_program = [
    ("LDI",128-8),
    ("STA",0x0e), # x座標
    ("LDI",180-8),
    ("STA",0x0f), # y座標
    ("LABEL", "main_loop"),
        # VBlank待ち
        ("LABEL", "wait_vblank"),
            ("LDA", 0x03),
            ("AND", 0x01),
            ("JZ", "wait_vblank"),
        ("LDI", 0),
        ("STA", 0x03),# フラグを0にしておく
        # キーボード状態反映
        ("LDA", 0x04),
        ("AND",0x1), # LEFT
        ("JZ","KRIGHT"),
            ("LDA",0x0e),# x座標
            ("SUB",0x1),
            ("STA",0x0e),# x座標
        ("LABEL", "KRIGHT"),
        ("LDA", 0x04),
        ("AND", 0x2), # RIGHT
        ("JZ","KUP"),
            ("LDA",0x0e),# x座標
            ("ADD",0x1),
            ("STA",0x0e),# x座標
        ("LABEL", "KUP"),
        ("LDA", 0x04),
        ("AND", 0x4), # UP
        ("JZ","KDOWN"),
            ("LDA",0x0f),# y座標
            ("SUB",0x1),
            ("STA",0x0f),# y座標
        ("LABEL", "KDOWN"),
        ("LDA", 0x04),
        ("AND", 0x8), # DOWN
        ("JZ","KEND"),
            ("LDA",0x0f),# y座標
            ("ADD",0x1),
            ("STA",0x0f),# y座標
        ("LABEL", "KEND"),
    ("JMP", "main_loop"),
]

# 割り込みハンドラ
interrupt_handler = [
    ("PUSHA",),
    ("IN", 0x00),      # IRQ status読む
    # VBLANK判定
    ("AND", 0x2),
    ("JNZ", "check_keyboard"),
        # VBLANK処理
        ("LDI", 1),
        ("STA", 0x03),
        ("POPA",),
        ("IRET",),
    # KEYBOARD処理
    ("LABEL", "check_keyboard"),
        ("IN", 0x10),      # キーボードステータス読む
        ("STA", 0x04),
        ("POPA",),
        ("IRET",),
]
main(main_program, interrupt_handler)
