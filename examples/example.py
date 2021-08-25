import sys
sys.path.insert(0, '/home/nik/Desktop/progetti/fem/femmpy')
import femmpy

fem = femmpy.femm_file()  # initialize file generator
# add iron square with vertices on the specified coordinates
# fem.polygon([[1, 0], [0, 0], [0, 1], [1, 1]], 'iron')
# add circuit named lol, real part of current is 2Amps, imaginary part is 0Amps, circuit type: 1 for series 0 for parallel
# fem.circuit("lol", 2, 0, 1)
# add left part of the coil made of 18AWG copper wire, circuit id is 1, the coil has 100 entering windings
# fem.polygon([[0, 0], [-1, 0], [-1, 1], [0, 1]], '18AWG', 1, 100)
# add right part of the coil made of 18AWG copper wire, circuit id is 1, the coil has 100 exiting windings
# fem.polygon([[2, 0], [1, 0], [1, 1], [2, 1]], '18AWG', 1, -100)

fem.polygon([[0, 0], [-1, 0], [-1, 1], [0, 1]], 'iron')
fem.polygon([[2, 0], [1, 0], [1, 1], [2, 1]], 'N55')

# GENERATE FEM FILE
try:
    # generate .fem file
    fem.generate("./example.fem")
    # mesh the geometry and solve
    fem.solve()
    # save image with plotted magnetic field
    fem.save_plot("./example.jpg")
except RuntimeError as e:
    print(e)
