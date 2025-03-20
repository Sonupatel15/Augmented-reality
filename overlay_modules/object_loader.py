class OBJ:
    def __init__(self, filename, swapyz=False):
        self.vertices, self.normals, self.texcoords, self.faces = [], [], [], []
        with open(filename, "r") as file:
            for line in file:
                if line.startswith("#"):
                    continue
                values = line.split()
                if not values:
                    continue
                if values[0] == "v":
                    v = list(map(float, values[1:4]))
                    self.vertices.append(v if not swapyz else (v[0], v[2], v[1]))
                elif values[0] == "vn":
                    v = list(map(float, values[1:4]))
                    self.normals.append(v if not swapyz else (v[0], v[2], v[1]))
                elif values[0] == "vt":
                    self.texcoords.append(list(map(float, values[1:3])))
                elif values[0] == "f":
                    face, texcoords, norms = [], [], []
                    for v in values[1:]:
                        w = v.split("/")
                        face.append(int(w[0]))
                        texcoords.append(int(w[1]) if len(w) >= 2 and w[1] else 0)
                        norms.append(int(w[2]) if len(w) >= 3 and w[2] else 0)
                    self.faces.append((face, norms, texcoords))