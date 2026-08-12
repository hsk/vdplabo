import sys
# SCREEN2 stripe table generator

screen_width, screen_height = 256, 192


def generate_stripe_table(horizon_y):
    result = []
    step = 16
    for y in range(screen_height):
        if y == horizon_y:
            result.append(step)
            continue

        if y < horizon_y:
            t = (horizon_y - 8) / (192 - 8 - 8)
            k = 8 * (1 - t) + 24 * t
            horizon_distance = horizon_y + k
            distance_from_horizon = horizon_distance - y
        else:
            t = (horizon_y - 8) / (192 - 8 - 8)
            k = 24 * (1 - t) + 8 * t
            horizon_distance = (screen_height - horizon_y + k)
            distance_from_horizon = horizon_distance - (screen_height - y)

        ground_z = step * 2 * horizon_distance / distance_from_horizon
        color = int(ground_z) & (step-1)
        result.append(color)

    return result

for horizon_y in range(8, 161, 8):
    data = generate_stripe_table(horizon_y)
    print(f"stripe_table_{horizon_y//8}: ; y = {horizon_y}")
    for i in range(0, 192, 16):
        chunk = data[i:i + 16]
        values = ",".join(str(v) for v in chunk)
        print(f"    db {values}")

    print()

print("stripe_tables:")
for horizon_y in range(8, 161, 8):
    print(f"    dw stripe_table_{horizon_y//8}")
