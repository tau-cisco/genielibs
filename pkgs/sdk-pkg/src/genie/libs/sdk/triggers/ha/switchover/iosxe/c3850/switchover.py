'''IOSXE implementation for Switchover triggers'''

# import python
import logging

# import ats
from ats import aetest
from ats.utils.objects import R

# Genie Libs
from genie.libs.sdk.libs.utils.mapping import Mapping
from genie.libs.sdk.triggers.ha.ha import \
                       TriggerSwitchover as CommonSwitchover

# from genie.libs import parser
from genie.libs.parser.iosxe.show_platform import ShowPlatform

log = logging.getLogger(__name__)

# Trigger required data settings
# Which key to exclude for Platform Ops comparison
platform_exclude = ['maker', 'main_mem', 'switchover_reason', 'issu',
                    'sn', 'config_register', 'rp_uptime', 'chassis_sn']


class TriggerSwitchover(CommonSwitchover):
    """Do switchover on device."""
    
    __description__ = """Do switchover on device.

    trigger_datafile:
        Mandatory:
            timeout: 
                max_time (`int`): Maximum wait time for the trigger,
                                in second. Default: 180
                interval (`int`): Wait time between iteration when looping is needed,
                                in second. Default: 15
        Optional:
            tgn_timeout (`int`): Maximum wait time for all traffic threads to be
                                 restored to the reference rate,
                                 in second. Default: 60
            tgn_delay (`int`): Wait time between each poll to verify if traffic is resumed,
                               in second. Default: 10

    steps:
        1. Learn Platform Ops object and store the "active" RP and "standby" RP
           if has any, otherwise, SKIP the trigger
        2. Do switchover by command "redundancy force-switchover"
        3. Learn Platform Ops again and verify the roles of 
           "active" RP and "standby" RP are swapped,
           and verify left attributes from the ops are the same as the Ops in step 1
        4. Update platform PTS if feature pts is enabled,
           Update global/local veirifications if enabled

    """

    @aetest.setup
    def verify_prerequisite(self, uut, abstract, steps, timeout):
        '''Learn Ops object and verify the requirements.

           If the requirements are not satisfied, then skip to the next
           testcase.

           Args:
               uut (`obj`): Device object.
               abstract (`obj`): Abstract object.
               steps (`step obj`): aetest step object
               timeout (`timeout obj`): Timeout Object

           Returns:
               None

           Raises:
               pyATS Results
        '''
        self.timeout = timeout
        try:
            self.pre_snap = self.mapping.learn_ops(device=uut,
                                                   abstract=abstract,
                                                   steps=steps,
                                                   timeout=self.timeout)
        except Exception as e:
            self.skipped('Cannot learn the feature', from_exception=e,
                         goto=['next_tc'])

        # get and store the member priority list
        try:
            out = ShowPlatform(device=uut).parse()
            # inital priority storage
            priority_dict = {}
            priority_list = []
            if 'slot' in out:
                for slot in out['slot']:
                    for rp in out['slot'][slot]['rp']:
                        if out['slot'][slot]['rp'][rp]['role'] == 'Member':
                            priority_dict[slot] = \
                                out['slot'][slot]['rp'][rp]['priority']
                            priority_list.append(out['slot'][slot]['rp'][rp]['priority'])
                            
                if len(list(set(priority_list))) != 1:
                    # sorted the slot priority
                    priority_list = sorted(priority_dict.items(), key=lambda x: x[1])

                    # update the verify_ops requirements
                    for ops, requirements in self.mapping._verify_ops_dict.items():
                        if 'platform' in ops:
                            self.mapping._verify_ops_dict[ops]['requirements'].append(
                                ['slot', 'rp', '{}'.format(priority_list[-1][0]),
                                 'swstack_role', 'Standby'])
                else:                    
                    # update the verify_ops requirements
                    for ops, requirements in self.mapping._verify_ops_dict.items():
                        if 'platform' in ops:
                            self.mapping._verify_ops_dict[ops]['requirements'].append(
                                ['slot', 'rp', '(?P<members>.*)',
                                 'swstack_role', '(Standby|Member)'])
        except Exception as e:
            log.warn('Cannot get the member priority. \n{}'.format(str(e)))


    # Mapping of Information between Ops and Conf
    # Also permit to dictates which key to verify
    mapping = Mapping(requirements={'ops.platform.platform.Platform':{
                                        'requirements': [\
                                            [['slot', 'rp', '(?P<active_rp>.*)',
                                              'swstack_role', 'Active'],
                                             ['slot', 'rp', '(?P<active_rp>.*)',
                                              'state', 'Ready']],
                                            [['slot', 'rp', '(?P<standby_rp>.*)',
                                              'swstack_role', 'Standby'],
                                             ['slot', 'rp', '(?P<standby_rp>.*)',
                                              'state', 'Ready']],
                                            [['slot', 'rp', '(?P<members>.*)',
                                              'swstack_role', 'Member'],
                                             ['slot', 'rp', '(?P<members>.*)',
                                              'state', 'Ready']],
                                            [['redundancy_communication', True]],
                                          ],
                                        'exclude': platform_exclude}},
                      verify_ops={'ops.platform.platform.Platform':{
                                      'requirements': [\
                                          ['slot', 'rp', '(?P<active_rp>.*)',
                                           'swstack_role', 'Member'],
                                          ['slot', 'rp', '(?P<standby_rp>.*)',
                                           'swstack_role', 'Active']],
                                    'exclude': platform_exclude}},
                      num_values={'active_rp':1, 'standby_rp':1, 'members': 'all'})