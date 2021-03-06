'''
Implementation for OSPF process restart triggers
'''

# Genie Libs
from genie.libs.sdk.triggers.processrestart.processrestart import TriggerProcessRestart


class TriggerProcessCliRestartOspf(TriggerProcessRestart):
    """Restart the running OSPF process(es) with CLI command "restart ospf <process>" """
    
    __description__ = """Restart the running OSPF process(es) with CLI command "restart ospf <process>"

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
        1. Learn OSPF process(es) with command "show system internal sysmgr service name ospf",
           and store the "running" process(es) if has any, otherwise, SKIP the trigger
        2. Restart the learned OSPF process(es) from step 1 with command "restart ospf <process>"
        3. Verify the pid of OSPF process(es) from step 2 is changed,
           and restart count of OSPF process(es) from step 2 is increased by 1

    """
    process = 'ospf'
    method = 'cli'
    verify_exclude = ['last_restart_date', 'state_start_date',
                      'last_terminate_reason', 'reboot_state',
                      'previous_pid']

class TriggerProcessCrashRestartOspf(TriggerProcessRestart):
    """Restart the running OSPF process(es) with linux command "kill -6 <process>",
    expecting process crashes and generates a core."""

    __description__ = """Restart the running OSPF process(es) with linux command "kill -6 <process>",
    expecting process crashes and generates a core.

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
        1. Learn OSPF process(es) with command "show system internal sysmgr service name ospf",
           and store the "running" process(es) if has any, otherwise, SKIP the trigger
        2. Restart the learned OSPF process(es) from step 1 with command "kill -6 <process>"
           in linux shell mode
        3. Verify the pid of OSPF process(es) from step 2 is changed,
           restart count of OSPF process(es) from step 2 is increased by 1,
           the count of "SYSMGR-2-SERVICE_CRASHED:" in log is 1 per OSPF process from step 2,
           and only 1 core generated on ospf per OSPF process from step 2

    """
    process = 'ospf'
    method = 'crash'
    crash_method = '6'
    verify_exclude = ['last_restart_date', 'state_start_date',
                      'last_terminate_reason', 'reboot_state',
                      'previous_pid']

class TriggerProcessKillRestartOspf(TriggerProcessRestart):
    """Restart the running OSPF process(es) with Linux command "kill -9 <process>" """

    __description__ = """Restart the running OSPF process(es) with Linux command "kill -9 <process>"

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
        1. Learn OSPF process(es) with command "show system internal sysmgr service name ospf",
           and store the "running" process(es) if has any, otherwise, SKIP the trigger
        2. Restart the learned OSPF process(es) from step 1 with command "kill -9 <process>"
           in linux shell mode
        3. Verify the pid of OSPF process(es) from step 2 is changed,
           and restart count of OSPF process(es) from step 2 is increased by 1

    """
    process = 'ospf'
    method = 'crash'
    crash_method = '9'
    verify_exclude = ['last_restart_date', 'state_start_date',
                      'last_terminate_reason', 'reboot_state',
                      'previous_pid']
