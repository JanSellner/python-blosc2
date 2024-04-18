#######################################################################
# Copyright (c) 2019-present, Blosc Development Team <blosc@blosc.org>
# All rights reserved.
#
# This source code is licensed under a BSD-style license (found in the
# LICENSE file in the root directory of this source tree)
#######################################################################

# This shows how to evaluate expressions with NDArray instances as operands.

import numpy as np
import blosc2
import numba as nb


shape = (13, 13)
dtype = np.float64

# Create a NDArray from a NumPy array
npa = np.linspace(0, 1, np.prod(shape)).reshape(shape)
npc = npa + 1

#a = blosc2.SChunk()
#a.append_data(npa)

a = blosc2.asarray(npa)

# Get a LazyExpr instance
#c = a + 1
# Evaluate!  Output is a NDArray
#d = c.evaluate()
# Check
#assert np.allclose(d[:], npc)


@nb.jit(nopython=True, parallel=True)
def func_numba(inputs_tuple, output, offset):
    x = inputs_tuple[0]
    output[:] = x + 1
    # out = np.empty(x.shape, x.dtype)
    # for i in nb.prange(x.shape[0]):
    #     for j in nb.prange(x.shape[1]):
    #         out[i, j] = x[i, j] + 1
    # return out

# nb_res = func_numba(npa)

chunks = [10, 10]
expr = blosc2.expr_from_udf(func_numba, ((npa, npa.dtype), ), npa.dtype, chunks=chunks, blocks=chunks)
res = expr.eval()
print(res.info)


# print(npa)
# print(res[:])
# print(npc)

#assert np.allclose(res[...], npc)
tol = 1e-5 if dtype is np.float32 else 1e-14
if dtype in (np.float32, np.float64):
    np.testing.assert_allclose(res[...], npc, rtol=tol, atol=tol)
