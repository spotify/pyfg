import unittest
from pyFG.fortios import FortiOS
from pyFG.forticonfig import FortiConfig
from pyFG.exceptions import CommandExecutionException, FailedCommit, ForcedCommit
import config
import random


class TestFortiOS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = FortiOS(config.vm_ip, vdom='test_vdom', username=config.username, password=config.password)
        cls.device.open()

        with open(config.config_file_1, 'r') as f:
            cls.config_1 = f.readlines()
        with open(config.config_file_2, 'r') as f:
            cls.config_2 = f.readlines()

    @classmethod
    def tearDownClass(cls):
        cls.device.close()
        pass

    def setUp(self):
        self.device.running_config = FortiConfig('running', vdom='test_vdom')
        self.device.candidate_config = FortiConfig('candidate', vdom='test_vdom')

    def test_execute_command_correctly(self):
        cmd = 'conf vdom\nedit test_vdom\nshow system interface'
        output = self.device.execute_command(cmd)
        self.assertGreater(len(output), 0)

    def test_execute_command_detect_error(self):
        cmd = 'show system interfacc'
        self.assertRaises(CommandExecutionException, self.device.execute_command, cmd)

    def test_load_a_single_block_of_config_from_device(self):
        config_block = 'system interface'
        self.device.load_config(path=config_block)
        self.assertEqual(len(self.device.running_config.sub_blocks), 1)
        self.assertEqual(len(self.device.candidate_config.sub_blocks), 1)

    def test_load_full_config_from_device_in_running(self):
        config_block = 'full-config'
        self.device.load_config(path=config_block, empty_candidate=True)
        self.assertGreater(len(self.device.running_config.sub_blocks), 0)
        # Candidate must be empty
        self.assertEqual(len(self.device.candidate_config.sub_blocks), 0)

    def test_load_config_from_file(self):
        self.device.load_config(config_text=self.config_1, empty_candidate=True)
        self.assertGreater(len(self.device.running_config.sub_blocks), 0)
        # Candidate must be empty
        self.assertEqual(len(self.device.candidate_config.sub_blocks), 0)

    def test_load_config_from_file_in_candidate(self):
        self.device.load_config(config_text=self.config_1, in_candidate=True)

        self.assertGreater(len(self.device.candidate_config.sub_blocks), 0)
        # Running must be empty
        self.assertEqual(len(self.device.running_config.sub_blocks), 0)

    def test_load_config_from_file_in_both(self):
        self.device.load_config(config_text=self.config_1)
        cand_ip = self.device.candidate_config['system interface']['port2'].get_param('ip')
        runn_ip = self.device.running_config['system interface']['port2'].get_param('ip')
        self.assertEqual(cand_ip, runn_ip)

    def test_compare_equal_configs(self):
        self.device.load_config(config_text=self.config_1)
        result = self.device.compare_config()
        # If they are equal, we should have gotten an empty string
        self.assertEqual(len(result), 0)

    def test_compare_equal_configs_in_text(self):
        self.device.load_config(config_text=self.config_1)
        result = self.device.compare_config(text=True)

        for line in result.splitlines():
            self.assertEqual(line[0], ' ')

    def test_compare_different_configs(self):
        self.device.load_config(config_text=self.config_1, empty_candidate=True)
        self.device.load_config(config_text=self.config_2, in_candidate=True)
        result = self.device.compare_config()
        self.assertGreater(len(result), 0)

    def test_compare_different_configs_in_text(self):
        self.device.load_config(config_text=self.config_1, empty_candidate=True)
        result = self.device.compare_config(text=True)

        for line in result.splitlines():
            self.assertNotEqual(line[0], ' ')

    def test_successful_commit(self):
        random_string = ''.join(random.choice('abcde ') for _ in range(10))
        self.device.load_config('system interface')
        self.device.candidate_config['system interface']['port1'].set_param('description', '"%s"' % random_string)

        pre_diff = self.device.compare_config()
        self.device.commit()
        post_diff = self.device.compare_config()

        # The previous diff should contain something
        self.assertGreater(len(pre_diff), 0)
        # The diff after the commit should be empty
        self.assertEqual(len(post_diff), 0)

    def test_failed_commit(self):
        random_string = ' '.join(random.choice('abcde') for _ in range(5))

        self.device.load_config('system interface')
        self.device.candidate_config['system interface']['port1'].set_param('description', '"%s"' % random_string)

        #This change will failed during the commit because we are missing the double quotes
        self.device.candidate_config['system interface']['port2'].set_param('description', '%s' % random_string)

        pre_diff = self.device.compare_config()
        self.assertRaises(FailedCommit, self.device.commit)
        post_diff = self.device.compare_config()

        # Both diffs have to be equal
        self.assertEqual(pre_diff, post_diff)

    def test_failed_commit_with_force(self):
        random_string = ' '.join(random.choice('abcde') for _ in range(5))

        self.device.load_config('system interface')
        self.device.candidate_config['system interface']['port1'].set_param('description', '"%s"' % random_string)

        #This change will failed during the commit because we are missing the double quotes
        self.device.candidate_config['system interface']['port2'].set_param('description', '%s' % random_string)

        pre_diff = self.device.compare_config()
        self.assertRaises(ForcedCommit, self.device.commit, force=True)
        post_diff = self.device.compare_config()

        # Both diffs have to be equal
        self.assertNotEqual(pre_diff, post_diff)

    def test_commit_with_retry_when_deleting(self):
        # First we make sure we have the config we want to delete
        starting_config = '''
conf vdom
  edit test_vdom
    config router route-map
        edit "test"
            set comments "asd asdad"
        next
    end

    config router bgp
            config neighbor
                edit "192.168.123.23"
                    set remote-as 65555
                    set route-map-in "test"
                next
            end
    end
end
'''
        self.device.commit(config_text=starting_config)
        self.device.load_config('router route-map')
        self.device.load_config('router bgp')
        self.device.candidate_config['router route-map'].del_block('test')
        self.device.candidate_config['router bgp']['neighbor'].del_block('192.168.123.23')

        pre_diff = self.device.compare_config()
        self.device.commit()
        post_diff = self.device.compare_config()

        # The previous diff should contain something
        self.assertGreater(len(pre_diff), 0)
        # The diff after the commit should be empty
        self.assertEqual(len(post_diff), 0)

    def test_commit_with_retry_when_adding(self):
        # First we make sure we don't have the config we want to add
        starting_config = '''
conf vdom
  edit test_vdom
     config router bgp
            config neighbor
                del "172.20.213.23"
                edit "2.2.2.2"
                    set remote-as 123
                    set shutdown enable
                end
            end

     end
     config router route-map
        del "test4"
        edit "dummy"
            set comments "asd"
        next
        end
end
'''
        try:
            self.device.commit(config_text=starting_config)
        except FailedCommit:
            pass

        self.device.load_config('router bgp')
        self.device.load_config('router route-map')

        neigh = FortiConfig('172.20.213.23', 'edit')
        neigh.set_param('remote-as', 65555)
        neigh.set_param('route-map-in', 'test4')
        self.device.candidate_config['router bgp']['neighbor']['172.20.213.23'] = neigh

        route_map = FortiConfig('test4', 'edit')
        route_map.set_param('comments', '"bla bla bla"')
        self.device.candidate_config['router route-map']['test4'] = route_map

        pre_diff = self.device.compare_config()
        self.device.commit()
        post_diff = self.device.compare_config()

        # The previous diff should contain something
        self.assertGreater(len(pre_diff), 0)
        # The diff after the commit should be empty
        self.assertEqual(len(post_diff), 0)
