import femmpy

fem = femmpy.femm_file()
fem.polygon([[1, 0], [0, 0], [0, 1], [1, 1]], 'iron')
fem.circuit("lol", 2, 0, 1)
fem.polygon([[0, 0], [-1, 0], [-1, 1], [0, 1]], '18AWG', 1, 100)
fem.polygon([[2, 0], [1, 0], [1, 1], [2, 1]], '18AWG', 1, -100)

# GENERATE FEM FILE
try:
    fem.generate("./example.fem")
    fem.solve()
    fem.save_plot("./example.jpg")
except RuntimeError as e:
    print(e)
