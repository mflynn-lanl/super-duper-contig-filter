# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from mcflynn_ContigFilter.mcflynn_ContigFilterImpl import mcflynn_ContigFilter
from mcflynn_ContigFilter.mcflynn_ContigFilterServer import MethodContext
from mcflynn_ContigFilter.authclient import KBaseAuth as _KBaseAuth

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.WorkspaceClient import Workspace


class mcflynn_ContigFilterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('mcflynn_ContigFilter'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'mcflynn_ContigFilter',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = mcflynn_ContigFilter(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa
        cls.prepareTestData()

    @classmethod
    def prepareTestData(cls):
        """This function creates an assembly object for testing"""
        fasta_content = '>seq1 something soemthing asdf\n' \
                        'agcttttcat\n' \
                        '>seq2\n' \
                        'agctt\n' \
                        '>seq3\n' \
                        'agcttttcatgg'

        filename = os.path.join(cls.scratch, 'test1.fasta')
        with open(filename, 'w') as f:
            f.write(fasta_content)
        assemblyUtil = AssemblyUtil(cls.callback_url)
        cls.assembly_ref = assemblyUtil.save_assembly_from_fasta({
            'file': {'path': filename},
            'workspace_name': cls.wsName,
            'assembly_name': 'TestAssembly'
        })

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def skip_test_run_mcflynn_ContigFilter_ok(self):
        # call your implementation
        ret = self.serviceImpl.run_mcflynn_ContigFilter(self.ctx,
                                                {'workspace_name': self.wsName,
                                                 'assembly_input_ref': self.assembly_ref,
                                                 'min_length': 10
                                                 })

        # Validate the returned data
        self.assertEqual(ret[0]['n_initial_contigs'], 3)
        self.assertEqual(ret[0]['n_contigs_removed'], 1)
        self.assertEqual(ret[0]['n_contigs_remaining'], 2)

    def skip_test_run_mcflynn_ContigFilter_min_len_negative(self):
        with self.assertRaisesRegex(ValueError, 'min_length parameter cannot be negative'):
            self.serviceImpl.run_mcflynn_ContigFilter(self.ctx,
                                              {'workspace_name': self.wsName,
                                               'assembly_input_ref': '1/fake/3',
                                               'min_length': '-10'})

    def skip_test_run_mcflynn_ContigFilter_min_len_parse(self):
        with self.assertRaisesRegex(ValueError, 'Cannot parse integer from min_length parameter'):
            self.serviceImpl.run_mcflynn_ContigFilter(self.ctx,
                                              {'workspace_name': self.wsName,
                                               'assembly_input_ref': '1/fake/3',
                                               'min_length': 'ten'})

    def test_run_mcflynn_ContigFilter_max(self):
        ref = "79/16/1"
        result = self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, {
            'workspace_name': self.wsName,
            'assembly_input_ref': ref,
            'min_length': 100,
            'max_length': 1000000
        })
        print(result)

    def test_run_mcflynn_ContigFilter_max_len_negative(self):
        with self.assertRaisesRegex(ValueError, 'max_length parameter cannot be negative'):
            ref = "79/16/1"
            self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, {
                'workspace_name': self.wsName,
                'assembly_input_ref': ref,
                'min_length': 100,
                'max_length': -1000000
            })


    def test_run_mcflynn_ContigFilter_max_lt_max_val(self):
        with self.assertRaisesRegex(ValueError, 'max_length parameter must be less than 9999999'):
            ref = "79/16/1"
            self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, {
                'workspace_name': self.wsName,
                'assembly_input_ref': ref,
                'min_length': 100,
                'max_length': 9999999 + 1
            })


    def test_run_mcflynn_ContigFilter_max_gt_min(self):
        with self.assertRaisesRegex(ValueError, 'max_length parameter 1 must be greater than min_length 1000'):
            ref = "79/16/1"
            self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, {
                'workspace_name': self.wsName,
                'assembly_input_ref': ref,
                'min_length': 1000,
                'max_length': 1
            })

    def test_run_mcflynn_ContigFilter_test_min(self):
        ref = "79/16/1"
        params = {
            'workspace_name': self.wsName,
            'assembly_input_ref': ref,
            'min_length': 200000,
            'max_length': 6000000
        }
        result = self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, params)
        self.assertEqual(result[0]['n_initial_contigs'], 2)
        self.assertEqual(result[0]['n_contigs_remaining'], 1)

    def test_run_mcflynn_ContigFilter_test_max(self):
        ref = "79/16/1"
        params = {
            'workspace_name': self.wsName,
            'assembly_input_ref': ref,
            'min_length': 100000,
            'max_length': 4000000
        }
        result = self.serviceImpl.run_mcflynn_ContigFilter_max(self.ctx, params)
        self.assertEqual(result[0]['n_initial_contigs'], 2)
        self.assertEqual(result[0]['n_contigs_remaining'], 1)