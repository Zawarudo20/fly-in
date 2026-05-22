from time import sleep
start = (0,0)
end = (10,15)

current = start
g = 0
paths = [current]
while current != end:
    x, y = current
    g += 1
    directions = [(x + 1, y),
                  (x - 1, y),
                  (x, y + 1),
                  (x, y - 1)]
    f = []
    for dir in directions:
        dx , dy = dir
        if (16 > dx >= 0 and 21 > dy >= 0):
            if end[0] > dx:
                x = end[0] - dx
            else:
                x = dx - end[0]
            if end[1] > dy:
                y = end[1] - dy
            else:
                y = dy - end[1]
            h = x + y
            print(f"{h}:{dir}")
            f.append({"position": dir, "f": h + g, "h": h})
    print("------------------------")
    next = f[0]
    for _ in f:
        if next["f"] > _["f"] or (next["f"] == _["f"] and next["h"] > _["h"]):
            next = _
    paths.append(next["position"])
    current = next["position"]
    sleep(1)
print(paths)