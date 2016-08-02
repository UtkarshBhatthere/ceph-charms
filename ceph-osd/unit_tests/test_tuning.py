__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'
from mock import patch, call
import test_utils
from ceph.ceph import ceph

TO_PATCH = [
    'hookenv',
    'status_set',
    'subprocess',
    'log',
]


class PerformanceTestCase(test_utils.CharmTestCase):
    def setUp(self):
        super(PerformanceTestCase, self).setUp(ceph, TO_PATCH)

    def test_tune_nic(self):
        with patch('ceph.ceph.ceph.get_link_speed', return_value=10000):
            with patch('ceph.ceph.ceph.save_sysctls') as save_sysctls:
                ceph.tune_nic('eth0')
                save_sysctls.assert_has_calls(
                    [
                        call(
                            save_location='/etc/sysctl.d/'
                                          '51-ceph-osd-charm-eth0.conf',
                            sysctl_dict={
                                'net.core.rmem_max': 524287,
                                'net.core.wmem_max': 524287,
                                'net.core.rmem_default': 524287,
                                'net.ipv4.tcp_wmem':
                                    '10000000 10000000 10000000',
                                'net.core.netdev_max_backlog': 300000,
                                'net.core.optmem_max': 524287,
                                'net.ipv4.tcp_mem':
                                    '10000000 10000000 10000000',
                                'net.ipv4.tcp_rmem':
                                    '10000000 10000000 10000000',
                                'net.core.wmem_default': 524287})
                    ])
                self.status_set.assert_has_calls(
                    [
                        call('maintenance', 'Tuning device eth0'),
                    ])

    def test_get_block_uuid(self):
        self.subprocess.check_output.return_value = \
            'UUID=378f3c86-b21a-4172-832d-e2b3d4bc7511\nTYPE=ext2\n'
        uuid = ceph.get_block_uuid('/dev/sda1')
        self.assertEqual(uuid, '378f3c86-b21a-4172-832d-e2b3d4bc7511')

    @patch('ceph.ceph.ceph.persist_settings')
    @patch('ceph.ceph.ceph.set_hdd_read_ahead')
    @patch('ceph.ceph.ceph.get_max_sectors_kb')
    @patch('ceph.ceph.ceph.get_max_hw_sectors_kb')
    @patch('ceph.ceph.ceph.set_max_sectors_kb')
    @patch('ceph.ceph.ceph.get_block_uuid')
    def test_tune_dev(self,
                      block_uuid,
                      set_max_sectors_kb,
                      get_max_hw_sectors_kb,
                      get_max_sectors_kb,
                      set_hdd_read_ahead,
                      persist_settings):
        self.hookenv.config.return_value = 712
        block_uuid.return_value = '378f3c86-b21a-4172-832d-e2b3d4bc7511'
        set_hdd_read_ahead.return_value = None
        get_max_sectors_kb.return_value = 512
        get_max_hw_sectors_kb.return_value = 1024
        ceph.tune_dev('/dev/sda')
        # The config value was lower than the hardware value.
        # We use the lower value.  The user wants 712 but the hw supports
        # 1K
        set_max_sectors_kb.assert_called_with(
            dev_name='sda', max_sectors_size=712
        )
        persist_settings.assert_called_with(
            settings_dict={'drive_settings': {
                '378f3c86-b21a-4172-832d-e2b3d4bc7511': {
                    'read_ahead_sect': 712}}}
        )
        self.status_set.assert_has_calls([
            call('maintenance', 'Tuning device /dev/sda'),
            call('maintenance', 'Finished tuning device /dev/sda')
        ])

    @patch('ceph.ceph.ceph.persist_settings')
    @patch('ceph.ceph.ceph.set_hdd_read_ahead')
    @patch('ceph.ceph.ceph.get_max_sectors_kb')
    @patch('ceph.ceph.ceph.get_max_hw_sectors_kb')
    @patch('ceph.ceph.ceph.set_max_sectors_kb')
    @patch('ceph.ceph.ceph.get_block_uuid')
    def test_tune_dev_2(self,
                        block_uuid,
                        set_max_sectors_kb,
                        get_max_hw_sectors_kb,
                        get_max_sectors_kb,
                        set_hdd_read_ahead,
                        persist_settings):
        self.hookenv.config.return_value = 2048
        block_uuid.return_value = '378f3c86-b21a-4172-832d-e2b3d4bc7511'
        set_hdd_read_ahead.return_value = None
        get_max_sectors_kb.return_value = 512
        get_max_hw_sectors_kb.return_value = 1024
        ceph.tune_dev('/dev/sda')
        # The config value was higher than the hardware value.
        # We use the lower value.  The user wants 2K but the hw only support 1K
        set_max_sectors_kb.assert_called_with(
            dev_name='sda', max_sectors_size=1024
        )
        persist_settings.assert_called_with(
            settings_dict={'drive_settings': {
                '378f3c86-b21a-4172-832d-e2b3d4bc7511': {
                    'read_ahead_sect': 1024}}}
        )
        self.status_set.assert_has_calls([
            call('maintenance', 'Tuning device /dev/sda'),
            call('maintenance', 'Finished tuning device /dev/sda')
        ])

    def test_set_hdd_read_ahead(self):
        ceph.set_hdd_read_ahead(dev_name='/dev/sda')
        self.subprocess.check_output.assert_called_with(
            ['hdparm', '-a256', '/dev/sda']
        )
