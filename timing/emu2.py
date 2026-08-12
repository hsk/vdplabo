import pygame
class CPU:
    def __init__(self):
        self.pc = 0x100
        self.acc = 0
        self.zero_flag = False
        self.io = {}
        self.memory = {}
    def find_label(self, label_name):
        for addr, inst in self.memory.items():
            if isinstance(inst,tuple) and inst[0] == "LABEL" and inst[1] == label_name:
                return addr + 1
        raise Exception(f"Label not found: {label_name}")
    def jmp(self, label, flg = True, clock=8):
        if flg:
            self.pc = self.find_label(label) if isinstance(label, str) else label
            return clock
        return 4
    def io_write(self, addr, value):
        self.io[addr] = value
    def load_program(self, program, start=0):
        for i, inst in enumerate(program):
            self.memory[start + i] = inst
    def step(self):
        inst = self.memory.get(self.pc, ("NOP",))
        self.pc += 1
        match inst:
            case ("NOP",): return 1
            case ("LABEL",): return 1
            case ("LDI",v): self.acc = v; return 1
            case ("LDA",a): self.acc = self.memory.get(a, 0); return 2
            case ("STA",a): self.memory[a] = self.acc; return 2
            case ("ADD",v): self.acc += v; self.zero_flag = (self.acc == 0); return 4
            case ("SUB",v): self.acc -= v; self.zero_flag = (self.acc == 0); return 4
            case ("AND",v): self.acc &= v; self.zero_flag = (self.acc == 0); return 4
            case ("JMP",a): return self.jmp(a, True, 6)
            case ("JZ",a): return self.jmp(a, self.zero_flag)
            case ("JNZ",a): return self.jmp(a, not self.zero_flag)
            case ("IN",p): self.acc = self.io.get(p, 0); return 4
            case ("OUT",p): self.io_write(p, self.acc); return 4
    def update(self):
        # 1フレーム分CPU実行
        while True:
            inst = self.memory.get(self.pc, ("FRAME_END",))
            if inst == ("FRAME_END",):
                self.pc += 1
                break
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
        self.state = state
def main(main_program):
    cpu = CPU()
    cpu.load_program(main_program, 0x0100)
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
        # キーボード状態取得
        ("IN", 0x10),
        ("STA", 0x04),
        # LEFT
        ("LDA", 0x04),
        ("AND",0x1),
        ("JZ","end_left"),
            ("LDA",0x0e),
            ("SUB",0x1),
            ("STA",0x0e),
        ("LABEL", "end_left"),
        # RIGHT
        ("LDA", 0x04),
        ("AND", 0x2),
        ("JZ","end_right"),
            ("LDA",0x0e),
            ("ADD",0x1),
            ("STA",0x0e),
        ("LABEL", "end_right"),
        # UP
        ("LDA", 0x04),
        ("AND", 0x4),
        ("JZ","end_up"),
            ("LDA",0x0f),
            ("SUB",0x1),
            ("STA",0x0f),
        ("LABEL", "end_up"),
        # DOWN
        ("LDA", 0x04),
        ("AND", 0x8),
        ("JZ","end_down"),
            ("LDA",0x0f),
            ("ADD",0x1),
            ("STA",0x0f),
        ("LABEL", "end_down"),
        # この命令で1フレーム終了
        ("FRAME_END",),
    ("JMP", "main_loop"),
]
main(main_program)
