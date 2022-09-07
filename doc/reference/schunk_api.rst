Super-chunk API
===============

.. currentmodule:: blosc2.SChunk

Methods
-------

.. autosummary::
   :toctree: autofiles/schunk/
   :nosignatures:

    SChunk.__init__
    SChunk.append_data
    SChunk.decompress_chunk
    SChunk.delete_chunk
    SChunk.get_chunk
    SChunk.insert_chunk
    SChunk.insert_data
    SChunk.update_chunk
    SChunk.update_data

vlmeta
======

.. currentmodule:: blosc2.SChunk

Class to access the variable length metalayers of a super-chunk.
    This class inherits from the
    `MutableMapping <https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping>`_
    class, so every method in this class is available. It
    behaves very similarly to a dictionary, and variable length metalayers can be appended
    in the typical way::

        schunk.vlmeta['vlmeta1'] = 'something'

    And can be retrieved similarly::
    And can be retrieved similarly::

        value = schunk.vlmeta['vlmeta1']

    Once added, a vlmeta can be deleted with::

        del schunk.vlmeta['vlmeta1']

    Moreover, a `getall()` method returns all the
    variable length metalayers as a dictionary.