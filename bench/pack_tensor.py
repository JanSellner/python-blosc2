########################################################################
#
#       Created: Oct 10, 2022
#       Author:  The Blosc development team - blosc@blosc.org
#
########################################################################


"""
Packaging tensors (PyTorch, TensorFlow) larger than 2 GB.
"""
import io
import sys
import time
import numpy as np
import blosc2
import torch
import tensorflow as tf


NREP = 1
# N = int(4e8 - 2**27)  # larger than 2 GB
N = int(1e8)

store = True
if len(sys.argv) > 1:
    store = True

#blosc2.set_nthreads(2)

print(f"Creating NumPy array with {float(N):.3g} float64 elements...")
in_ = np.arange(N, dtype=np.float64)

if store:
    tt = tf.constant(in_)
    th = torch.from_numpy(in_)

    # # Standard TensorFlow serialization
    # c = None
    # ctic = time.time()
    # for i in range(NREP):
    #     c = tf.io.serialize_tensor(tt).numpy()
    # ctoc = time.time()
    # tc = (ctoc - ctic) / NREP
    # print(
    #     "  Time for tensorflow (io.serialize):   %.3f (%.2f GB/s)) "
    #     % (tc, ((N * 8 / tc) / 2 ** 30)), end=""
    # )
    # print("\tcr: %5.1fx" % (in_.size * in_.dtype.itemsize * 1.0 / len(c)))
    #
    # with open("serialize_tensorflow.bin", 'wb') as f:
    #     f.write(c)
    #
    # # Standard PyTorch serialization
    # c = None
    # buff = io.BytesIO()
    # ctic = time.time()
    # for i in range(NREP):
    #     torch.save(th, buff)
    # ctoc = time.time()
    # tc = (ctoc - ctic) / NREP
    # print(
    #     "  Time for torch (torch.save):   %.3f (%.2f GB/s)) "
    #     % (tc, ((N * 8 / tc) / 2 ** 30)), end=""
    # )
    # buff.seek(0)
    # c = buff.read()
    # print("\tcr: %5.1fx" % (in_.size * in_.dtype.itemsize * 1.0 / len(c)))
    #
    # with open("serialize_torch.bin", 'wb') as f:
    #     f.write(c)
    #
    codec = blosc2.Codec.BLOSCLZ
    # print(f"Storing with {codec}")
    cparams = {"codec": codec, "clevel": 9}

    c = None
    ctic = time.time()
    for i in range(NREP):
        _in = np.asarray(memoryview(tt))
        c = blosc2.pack_array2(_in, cparams=cparams)
    ctoc = time.time()
    tc = (ctoc - ctic) / NREP
    print(
        "  Time for tensorflow:   %.3f (%.2f GB/s)) "
        % (tc, ((N * 8 / tc) / 2 ** 30)), end=""
    )
    print("\tcr: %5.1fx" % (in_.size * in_.dtype.itemsize * 1.0 / len(c)))

    with open("pack_tensorflow.bl2", 'wb') as f:
        f.write(c)

    tt = torch.from_numpy(in_)
    c = None
    ctic = time.time()
    for i in range(NREP):
        #_in = np.asarray(th)
        #c = blosc2.pack_array2(_in, cparams=cparams)
        c = blosc2.pack_tensor(in_, cparams=cparams)
    ctoc = time.time()
    tc = (ctoc - ctic) / NREP
    print(
        "  Time for torch:   %.3f (%.2f GB/s)) "
        % (tc, ((N * 8 / tc) / 2 ** 30)), end=""
    )
    print("\tcr: %5.1fx" % (in_.size * in_.dtype.itemsize * 1.0 / len(c)))

    with open("pack_torch.bl2", 'wb') as f:
        f.write(c)

else:
    with open("serialize_tensorflow.bin", 'rb') as f:
        c = f.read()

    dtic = time.time()
    for i in range(NREP):
        tt = tf.io.parse_tensor(c, out_type=in_.dtype)
    dtoc = time.time()
    td = (dtoc - dtic) / NREP
    print(
        "  Time for parse_tensor (tensorflow):   %.3f s (%.2f GB/s)) "
        % (td, ((N * 8 / td) / 2 ** 30)),
    )
    del tt

    with open("serialize_torch.bin", 'rb') as f:
        buff = io.BytesIO(f.read())

    dtic = time.time()
    for i in range(NREP):
        tt = torch.load(buff)
    dtoc = time.time()
    td = (dtoc - dtic) / NREP
    print(
        "  Time for torch.load (torch):   %.3f s (%.2f GB/s)) "
        % (td, ((N * 8 / td) / 2 ** 30)),
    )
    del tt

    with open("pack_tensorflow.bl2", 'rb') as f:
        c = f.read()

    out = None
    dtic = time.time()
    for i in range(NREP):
        # out = blosc2.unpack_tensor(c)
        schunk = blosc2.schunk_from_cframe(c, False)
        dtype = schunk.vlmeta['dtype']
        shape = schunk.vlmeta['shape']
        out = np.empty(shape, dtype=dtype)
        schunk.get_slice(out=out)
        tt = tf.constant(out)

    dtoc = time.time()
    td = (dtoc - dtic) / NREP
    print(
        "  Time for unpack_tensor (tensorflow):   %.3f s (%.2f GB/s)) "
        % (td, ((N * 8 / td) / 2 ** 30)),
    )
    assert np.array_equal(in_, out)
    del out, tt

    with open("pack_torch.bl2", 'rb') as f:
        c = f.read()

    out = None
    dtic = time.time()
    for i in range(NREP):
        # out = blosc2.unpack_tensor(c)
        schunk = blosc2.schunk_from_cframe(c, False)
        dtype = schunk.vlmeta['dtype']
        shape = schunk.vlmeta['shape']
        out = np.empty(shape, dtype=dtype)
        schunk.get_slice(out=out)
        tt = torch.from_numpy(out)

    dtoc = time.time()

    td = (dtoc - dtic) / NREP
    print(
        "  Time for unpack_tensor (torch):   %.3f s (%.2f GB/s)) "
        % (td, ((N * 8 / td) / 2 ** 30)),
    )
    assert np.array_equal(in_, out)