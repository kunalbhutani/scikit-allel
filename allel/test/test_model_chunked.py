# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division


import unittest
import numpy as np
import bcolz
import h5py
from nose.tools import assert_raises, eq_ as eq


from allel.model.ndarray import GenotypeArray, HaplotypeArray, \
    AlleleCountsArray, VariantTable, FeatureTable
from allel.test.tools import assert_array_equal as aeq
from allel.test.test_model_api import GenotypeArrayInterface, \
    diploid_genotype_data, triploid_genotype_data, HaplotypeArrayInterface, \
    haplotype_data, allele_counts_data, AlleleCountsArrayInterface, \
    VariantTableInterface, variant_table_data, variant_table_dtype, \
    variant_table_names, feature_table_data, feature_table_dtype, \
    feature_table_names, FeatureTableInterface
import allel.model.chunked as chunked


class GenotypeChunkedArrayTests(GenotypeArrayInterface, unittest.TestCase):

    _class = chunked.GenotypeChunkedArray

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolzmem_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data, chunklen=2)
        return chunked.GenotypeChunkedArray(data)

    def test_constructor(self):

        # missing data arg
        with assert_raises(TypeError):
            # noinspection PyArgumentList
            chunked.GenotypeChunkedArray()

        # data has wrong dtype
        data = 'foo bar'
        with assert_raises(ValueError):
            chunked.GenotypeChunkedArray(data)

        # data has wrong dtype
        data = np.array([4., 5., 3.7])
        with assert_raises(ValueError):
            chunked.GenotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([1, 2, 3])
        with assert_raises(ValueError):
            chunked.GenotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([[1, 2], [3, 4]])  # use HaplotypeChunkedArray instead
        with assert_raises(ValueError):
            chunked.GenotypeChunkedArray(data)

        # diploid data (typed)
        g = self.setup_instance(np.array(diploid_genotype_data, dtype='i1'))
        aeq(diploid_genotype_data, g)
        eq(np.int8, g.dtype)

        # polyploid data (typed)
        g = self.setup_instance(np.array(triploid_genotype_data, dtype='i1'))
        aeq(triploid_genotype_data, g)
        eq(np.int8, g.dtype)

    def test_storage(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        # default is bcolz mem
        assert isinstance(g.data, bcolz.carray)
        assert g.data.rootdir is None, g.data.rootdir

    def test_slice_types(self):

        g = self.setup_instance(np.array(diploid_genotype_data, dtype='i1'))

        # row slice
        s = g[1:]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertIsInstance(s, GenotypeArray)

        # col slice
        s = g[:, 1:]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertIsInstance(s, GenotypeArray)

        # row index
        s = g[0]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # col index
        s = g[:, 0]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # ploidy index
        s = g[:, :, 0]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # item
        s = g[0, 0, 0]
        self.assertNotIsInstance(s, chunked.GenotypeChunkedArray)
        self.assertNotIsInstance(s, GenotypeArray)
        self.assertIsInstance(s, np.int8)

    def test_take(self):
        g = self.setup_instance(diploid_genotype_data)
        # take variants not in original order
        # not supported for carrays
        indices = [2, 0]
        with assert_raises(NotImplementedError):
            g.take(indices, axis=0)


class GenotypeChunkedArrayTestsBColzTmpStorage(GenotypeChunkedArrayTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolztmp_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data, chunklen=2)
        return chunked.GenotypeChunkedArray(data)

    def test_storage(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, bcolz.carray)
        assert g.data.rootdir is not None


class GenotypeChunkedArrayTestsBColzCustomStorage(GenotypeChunkedArrayTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.BcolzMemStorage(
            cparams=bcolz.cparams(cname='zlib', clevel=1))

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data, chunklen=2)
        return chunked.GenotypeChunkedArray(data)

    def test_storage(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, bcolz.carray)
        eq('zlib', g.data.cparams.cname)
        eq(1, g.data.cparams.clevel)


class GenotypeChunkedArrayTestsHDF5MemStorage(GenotypeChunkedArrayTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.hdf5mem_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data)
        return chunked.GenotypeChunkedArray(data)

    def test_storage(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, h5py.Dataset)


class GenotypeChunkedArrayTestsHDF5TmpStorage(GenotypeChunkedArrayTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.hdf5tmp_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data)
        return chunked.GenotypeChunkedArray(data)

    def test_storage(self):
        g = self.setup_instance(np.array(diploid_genotype_data))
        assert isinstance(g.data, h5py.Dataset)


class HaplotypeChunkedArrayTests(HaplotypeArrayInterface, unittest.TestCase):

    _class = chunked.HaplotypeChunkedArray

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolzmem_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data, chunklen=2)
        return chunked.HaplotypeChunkedArray(data)

    def test_constructor(self):

        # missing data arg
        with assert_raises(TypeError):
            # noinspection PyArgumentList
            chunked.HaplotypeChunkedArray()

        # data has wrong dtype
        data = 'foo bar'
        with assert_raises(ValueError):
            chunked.HaplotypeChunkedArray(data)

        # data has wrong dtype
        data = np.array([4., 5., 3.7])
        with assert_raises(ValueError):
            chunked.HaplotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([1, 2, 3])
        with assert_raises(ValueError):
            chunked.HaplotypeChunkedArray(data)

        # data has wrong dimensions
        data = np.array([[[1, 2], [3, 4]]])  # use GenotypeCArray instead
        with assert_raises(ValueError):
            chunked.HaplotypeChunkedArray(data)

        # typed data (typed)
        h = chunked.HaplotypeChunkedArray(np.array(haplotype_data, dtype='i1'))
        aeq(haplotype_data, h)
        eq(np.int8, h.dtype)

    def test_slice_types(self):

        h = self.setup_instance(np.array(haplotype_data, dtype='i1'))

        # row slice
        s = h[1:]
        self.assertNotIsInstance(s, chunked.HaplotypeChunkedArray)
        self.assertIsInstance(s, HaplotypeArray)

        # col slice
        s = h[:, 1:]
        self.assertNotIsInstance(s, chunked.HaplotypeChunkedArray)
        self.assertIsInstance(s, HaplotypeArray)

        # row index
        s = h[0]
        self.assertNotIsInstance(s, chunked.HaplotypeChunkedArray)
        self.assertNotIsInstance(s, HaplotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # col index
        s = h[:, 0]
        self.assertNotIsInstance(s, chunked.HaplotypeChunkedArray)
        self.assertNotIsInstance(s, HaplotypeArray)
        self.assertIsInstance(s, np.ndarray)

        # item
        s = h[0, 0]
        self.assertNotIsInstance(s, chunked.HaplotypeChunkedArray)
        self.assertNotIsInstance(s, HaplotypeArray)
        self.assertIsInstance(s, np.int8)


class AlleleCountsChunkedArrayTests(AlleleCountsArrayInterface,
                                    unittest.TestCase):

    _class = chunked.AlleleCountsChunkedArray

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolzmem_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data, chunklen=2)
        return chunked.AlleleCountsChunkedArray(data)

    def test_constructor(self):

        # missing data arg
        with assert_raises(TypeError):
            # noinspection PyArgumentList
            chunked.AlleleCountsChunkedArray()

        # data has wrong dtype
        data = 'foo bar'
        with assert_raises(ValueError):
            chunked.AlleleCountsChunkedArray(data)

        # data has wrong dtype
        data = np.array([4., 5., 3.7])
        with assert_raises(ValueError):
            chunked.AlleleCountsChunkedArray(data)

        # data has wrong dimensions
        data = np.array([1, 2, 3])
        with assert_raises(ValueError):
            chunked.AlleleCountsChunkedArray(data)

        # data has wrong dimensions
        data = np.array([[[1, 2], [3, 4]]])
        with assert_raises(ValueError):
            chunked.AlleleCountsChunkedArray(data)

        # typed data (typed)
        ac = chunked.AlleleCountsChunkedArray(np.array(allele_counts_data,
                                                       dtype='u1'))
        aeq(allele_counts_data, ac)
        eq(np.uint8, ac.dtype)

    def test_slice_types(self):

        ac = self.setup_instance(np.array(allele_counts_data, dtype='u2'))

        # row slice
        s = ac[1:]
        self.assertNotIsInstance(s, chunked.AlleleCountsChunkedArray)
        self.assertIsInstance(s, AlleleCountsArray)

        # col slice
        s = ac[:, 1:]
        self.assertNotIsInstance(s, chunked.AlleleCountsChunkedArray)
        self.assertNotIsInstance(s, AlleleCountsArray)
        self.assertIsInstance(s, np.ndarray)

        # row index
        s = ac[0]
        self.assertNotIsInstance(s, chunked.AlleleCountsChunkedArray)
        self.assertNotIsInstance(s, AlleleCountsArray)
        self.assertIsInstance(s, np.ndarray)

        # col index
        s = ac[:, 0]
        self.assertNotIsInstance(s, chunked.AlleleCountsChunkedArray)
        self.assertNotIsInstance(s, AlleleCountsArray)
        self.assertIsInstance(s, np.ndarray)

        # item
        s = ac[0, 0]
        self.assertNotIsInstance(s, chunked.AlleleCountsChunkedArray)
        self.assertNotIsInstance(s, AlleleCountsArray)
        self.assertIsInstance(s, np.uint16)


class AlleleCountsChunkedArrayTestsHDF5Mem(AlleleCountsChunkedArrayTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.hdf5mem_storage

    def setup_instance(self, data):
        data = chunked.storage_registry['default'].array(data)
        return chunked.AlleleCountsChunkedArray(data)


class VariantChunkedTableTests(VariantTableInterface, unittest.TestCase):

    _class = chunked.VariantChunkedTable

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolzmem_storage

    def setup_instance(self, data, **kwargs):
        data = chunked.storage_registry['default'].table(data, chunklen=2)
        return chunked.VariantChunkedTable(data, **kwargs)

    def test_storage(self):
        a = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = self.setup_instance(a)
        assert isinstance(vt.data, bcolz.ctable)

    def test_constructor(self):

        # missing data arg
        with self.assertRaises(TypeError):
            chunked.VariantChunkedTable()

        # recarray
        ra = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = chunked.VariantChunkedTable(ra)
        eq(5, len(vt))
        aeq(ra, vt)

        # dict
        d = {n: ra[n] for n in variant_table_names}
        vt = chunked.VariantChunkedTable(d, names=variant_table_names)
        eq(5, len(vt))
        aeq(ra, vt)

    def test_slice_types(self):
        ra = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = chunked.VariantChunkedTable(ra)

        # row slice
        s = vt[1:]
        self.assertNotIsInstance(s, chunked.VariantChunkedTable)
        self.assertIsInstance(s, VariantTable)

        # row index
        s = vt[0]
        self.assertNotIsInstance(s, chunked.VariantChunkedTable)
        self.assertNotIsInstance(s, VariantTable)
        self.assertIsInstance(s, (np.record, np.void, tuple))

        # col access
        s = vt['CHROM']
        self.assertNotIsInstance(s, chunked.VariantChunkedTable)
        self.assertNotIsInstance(s, VariantTable)
        self.assertIsInstance(s, chunked.ChunkedArray)

    def test_take(self):
        a = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = chunked.VariantChunkedTable(a)
        # take variants not in original order
        # not supported for carrays
        indices = [2, 0]
        with assert_raises(NotImplementedError):
            vt.take(indices)


class VariantChunkedTableTestsHDF5Storage(VariantChunkedTableTests):

    def setUp(self):
        chunked.storage_registry['default'] = chunked.hdf5mem_storage

    def setup_instance(self, data, **kwargs):
        data = chunked.storage_registry['default'].table(data)
        return chunked.VariantChunkedTable(data, **kwargs)

    def test_storage(self):
        a = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = self.setup_instance(a)
        assert isinstance(vt.data, h5py.Group)


class FeatureChunkedTableTests(FeatureTableInterface, unittest.TestCase):

    _class = chunked.FeatureChunkedTable

    def setUp(self):
        chunked.storage_registry['default'] = chunked.bcolzmem_storage

    def setup_instance(self, data, **kwargs):
        data = chunked.storage_registry['default'].table(data)
        return chunked.FeatureChunkedTable(data, **kwargs)

    def test_storage(self):
        a = np.rec.array(variant_table_data, dtype=variant_table_dtype)
        vt = self.setup_instance(a)
        assert isinstance(vt.data, bcolz.ctable)

    def test_constructor(self):

        # missing data arg
        with self.assertRaises(TypeError):
            chunked.FeatureChunkedTable()

        # recarray
        ra = np.rec.array(feature_table_data, dtype=feature_table_dtype)
        ft = chunked.FeatureChunkedTable(ra)
        eq(6, len(ft))
        aeq(ra, ft)

        # dict
        d = {n: ra[n] for n in feature_table_names}
        ft = chunked.FeatureChunkedTable(d, names=feature_table_names)
        eq(6, len(ft))
        aeq(ra, ft)

    def test_slice_types(self):
        ra = np.rec.array(feature_table_data, dtype=feature_table_dtype)
        ft = chunked.FeatureChunkedTable(ra)

        # row slice
        s = ft[1:]
        self.assertNotIsInstance(s, chunked.FeatureChunkedTable)
        self.assertIsInstance(s, FeatureTable)

        # row index
        s = ft[0]
        self.assertNotIsInstance(s, chunked.FeatureChunkedTable)
        self.assertNotIsInstance(s, FeatureTable)
        self.assertIsInstance(s, (np.record, np.void, tuple))

        # col access
        s = ft['seqid']
        self.assertNotIsInstance(s, chunked.FeatureChunkedTable)
        self.assertNotIsInstance(s, FeatureTable)
        self.assertIsInstance(s, chunked.ChunkedArray)
