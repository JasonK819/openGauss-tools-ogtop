# -*- coding: utf-8 -*-
""" session data storage calculation """
import copy
import json
import time

import db_util
import pandas as pd

pd.options.mode.chained_assignment = None


class SessionMain(object):

    def __init__(self, openGauss_option, sqls):
        """
       initialization session data
        :param openGauss_option: openGauss database operation object
        :param sqls: sql execute specified sql statement
        """
        data = openGauss_option.all_query_sql(sqls)
        try:
            session_df = pd.DataFrame(data)
            session_df.columns = ['datid', 'db_name', 'pid', 'usesysid', 'user_name', 'application_name', 'client_addr',
                                  'client_hostname', 'client_port', 'backend_start', 'xact_start', 'query_start',
                                  'state_change', 'waiting', 'enqueue', 'state', 'resource_pool', 'query_id', 'query',
                                  'pid1', 'n_commit', 'n_rollback', 'n_sql', 'n_table_scan', 'n_blocks_fetched',
                                  'n_physical_read_operation', 'n_shared_blocks_dirtied', 'n_local_blocks_dirtied',
                                  'n_shared_blocks_read', 'n_local_blocks_read', 'n_blocks_read_time',
                                  'n_blocks_write_time',
                                  'n_sort_in_memory', 'n_sort_in_disk', 'n_cu_mem_hit', 'n_cu_hdd_sync_read',
                                  'n_cu_hdd_asyn_read',
                                  'pid2', 'DB_TIME', 'CPU_TIME', 'EXECUTION_TIME', 'PARSE_TIME', 'PLAN_TIME',
                                  'REWRITE_TIME',
                                  'PL_EXECUTION_TIME', 'PL_COMPILATION_TIME', 'NET_SEND_TIME', 'DATA_IO_TIME',
                                  'pid3', 'wait_status', 'wait_event']

            res_session_df = session_df[['pid', 'state', 'waiting', 'user_name', 'application_name', 'client_addr',
                                         'db_name', 'xact_start', 'state_change', 'n_commit', 'n_rollback', 'n_sql',
                                         'n_table_scan',
                                         'n_blocks_fetched', 'n_physical_read_operation', 'n_shared_blocks_dirtied',
                                         'n_local_blocks_dirtied',
                                         'n_shared_blocks_read', 'n_local_blocks_read', 'n_blocks_read_time',
                                         'n_blocks_write_time',
                                         'n_sort_in_memory', 'n_sort_in_disk', 'n_cu_mem_hit', 'n_cu_hdd_sync_read',
                                         'n_cu_hdd_asyn_read',
                                         'CPU_TIME', 'DATA_IO_TIME', 'DB_TIME', 'EXECUTION_TIME', 'wait_status',
                                         'wait_event', 'query']]

            res_session_df.rename(
                columns={'state': 'current_state', 'xact_start': 'xact_start_time', 'state_change': 'state_change_time',
                         'CPU_TIME': 'cpu_time', 'DATA_IO_TIME': 'data_io_time', 'DB_TIME': 'db_time',
                         'EXECUTION_TIME': 'execute_time'}, inplace=True)

            values = {'db_time': 0, 'cpu_time': 0, 'execute_time': 0, 'data_io_time': 0, 'current_state': '-',
                      'db_name': '-', 'user_name': '-', 'application_name': '-', 'client_addr': '-',
                      'xact_start_time': '-', 'state_change_time': '-', 'waiting': '-', 'n_commit': 0,
                      'n_rollback': 0, 'n_sql': 0, 'n_table_scan': 0, 'n_blocks_fetched': 0,
                      'n_physical_read_operation': 0, 'n_shared_blocks_dirtied': 0, 'n_local_blocks_dirtied': 0,
                      'n_shared_blocks_read': 0, 'n_local_blocks_read': 0, 'n_blocks_read_time': 0,
                      'n_blocks_write_time': 0,
                      'n_sort_in_memory': 0, 'n_sort_in_disk': 0, 'n_cu_mem_hit': 0, 'n_cu_hdd_sync_read': 0,
                      'n_cu_hdd_asyn_read': 0
                      }
            res_session_df.fillna(value=values, inplace=True)

            res_session_df.replace(to_replace='None', value='-', inplace=True)
            res_session_df.fillna('-', inplace=True)
            res_session_df = res_session_df.reset_index()
            res_session_df.pop('index')
        except Exception as e:
            res_session_df = data
        self.de_part = res_session_df

    @staticmethod
    def intergrated_data(session_data):
        """
        calculate the increment，save the result to dictionary，transfer and display to the interface
        :param replication_data: refresh data this time
        :return: return the computer result
        """
        data_list = session_data[['pid', 'current_state', 'db_name', 'user_name', 'application_name', 'client_addr',
                                  'xact_start_time', 'state_change_time', 'waiting', 'db_time', 'cpu_time',
                                  'execute_time', 'data_io_time', 'wait_status', 'wait_event', 'query']].to_json(
            orient='records')
        data_session = (data_list[1:-1]).replace("},", "}!")
        data_session.split("!")
        data_session = json.loads(data_list)

        header_data = {
            "active session/session": db_util.progress_bar(
                int(session_data[session_data['current_state'] == 'active']['current_state'].count()) / int(
                    session_data['current_state'].count()) * 100),
            "n_commit": str(int(session_data['n_commit'].sum())),
            "n_blocks_fetched": str(int(session_data['n_blocks_fetched'].sum())),
            "n_rollback": str(int(session_data['n_rollback'].sum())),
            "n_physical_read_operation": str(int(session_data['n_physical_read_operation'].sum())),
            "n_sql": str(int(session_data['n_sql'].sum())),
            "n_shared_blocks_dirtied": str(int(session_data['n_shared_blocks_dirtied'].sum())),
            "n_table_scan": str(int(session_data['n_table_scan'].sum())),
            "n_cu_hdd_asyn_read": str(int(session_data['n_cu_hdd_asyn_read'].sum())),
            "n_local_blocks_dirtied": str(int(session_data['n_local_blocks_dirtied'].sum())),
            "n_shared_blocks_read": str(int(session_data['n_shared_blocks_read'].sum())),
            "n_local_blocks_read": str(int(session_data['n_local_blocks_read'].sum())),
            "n_blocks_read_time": str(int(session_data['n_blocks_read_time'].sum())),
            "n_blocks_write_time": str(int(session_data['n_blocks_write_time'].sum())),
            "n_sort_in_memory": str(int(session_data['n_sort_in_memory'].sum())),
            "n_sort_in_disk": str(int(session_data['n_sort_in_disk'].sum())),
            "n_cu_mem_hit": str(int(session_data['n_cu_mem_hit'].sum())),
            "n_cu_hdd_sync_read": str(int(session_data['n_cu_hdd_sync_read'].sum()))}

        return data_session, header_data

    @staticmethod
    def compute_delta(depart, heard_depart, old_depart, old_heard_depart):
        """
        calculate the increment，save the result to dictionary，transfer and display to the interface
        :param old_depart: last refresh data
        :param old_heard_depart:last refresh heard data
        :param depart: refresh data this time
        :param heard_depart:refresh heard data this time
        :return: return the computer result
        """
        depart_heard_depart = copy.deepcopy(heard_depart)
        depart_depart = copy.deepcopy(depart)
        old_depart_list = [d["pid"] for d in old_depart]
        new_depart_list = [d["pid"] for d in depart]
        now = time.time() * 1000
        for new_depart_pid in new_depart_list:
            new_index_num = new_depart_list.index(new_depart_pid)
            xact_start_time = depart[new_index_num].get("xact_start_time")
            state_change_time = depart[new_index_num].get("state_change_time")
            depart_depart[new_index_num]["xact_start_time"] = now - int(
                xact_start_time) if xact_start_time != "-" and int(xact_start_time) != "0" else 0
            depart_depart[new_index_num]["state_change_time"] = now - int(
                state_change_time) if state_change_time != "-" and int(state_change_time) != "0" else 0

            if new_depart_pid in old_depart_list:
                old_index_num = old_depart_list.index(new_depart_pid)
                db_time = depart[new_index_num].get("db_time")
                cpu_time = depart[new_index_num].get("cpu_time")
                execute_time = depart[new_index_num].get("execute_time")
                data_io_time = depart[new_index_num].get("data_io_time")
                old_db_time = old_depart[old_index_num].get("db_time")
                old_cpu_time = old_depart[old_index_num].get("cpu_time")
                old_execute_time = old_depart[old_index_num].get("execute_time")
                old_data_io_time = old_depart[old_index_num].get("data_io_time")
                depart_depart[new_index_num]["db_time"] = str(
                    round((int(db_time) - int(old_db_time)) / 1000000, 4) if round(
                        (int(db_time) - int(old_db_time)) / 1000000, 4) >= 0 else 0.0)
                depart_depart[new_index_num]["cpu_time"] = str(
                    round((int(cpu_time) - int(old_cpu_time)) / 1000000, 4) if round(
                        (int(cpu_time) - int(old_cpu_time)) / 1000000, 4) >= 0 else 0.0)
                depart_depart[new_index_num]["execute_time"] = str(
                    round((int(execute_time) - int(old_execute_time)) / 1000000, 4) if round(
                        (int(execute_time) - int(old_execute_time)) / 1000000, 4) >= 0 else 0.0)
                depart_depart[new_index_num]["data_io_time"] = str(
                    round((int(data_io_time) - int(old_data_io_time)) / 1000000, 4) if round(
                        (int(data_io_time) - int(old_data_io_time)) / 1000000, 4) >= 0 else 0.0)
            else:
                db_time = depart[new_index_num].get("db_time")
                cpu_time = depart[new_index_num].get("cpu_time")
                execute_time = depart[new_index_num].get("execute_time")
                data_io_time = depart[new_index_num].get("data_io_time")
                depart_depart[new_index_num]["db_time"] = str(round(int(db_time) / 1000000, 4))
                depart_depart[new_index_num]["cpu_time"] = str(round(int(cpu_time) / 1000000, 4))
                depart_depart[new_index_num]["execute_time"] = str(round(int(execute_time) / 1000000, 4))
                depart_depart[new_index_num]["data_io_time"] = str(round(int(data_io_time) / 1000000, 4))
        depart_heard_depart["n_commit"] = str(
            int(heard_depart["n_commit"]) - int(old_heard_depart["n_commit"]) if int(heard_depart["n_commit"]) - int(
                old_heard_depart["n_commit"]) > 0 else 0)
        depart_heard_depart["n_blocks_fetched"] = str(
            int(heard_depart["n_blocks_fetched"]) - int(old_heard_depart["n_blocks_fetched"]) if int(
                heard_depart["n_blocks_fetched"]) - int(old_heard_depart["n_blocks_fetched"]) > 0 else 0)
        depart_heard_depart["n_rollback"] = str(
            int(heard_depart["n_rollback"]) - int(old_heard_depart["n_rollback"]) if int(
                heard_depart["n_rollback"]) - int(old_heard_depart["n_rollback"]) > 0 else 0)
        depart_heard_depart["n_physical_read_operation"] = str(
            int(heard_depart["n_physical_read_operation"]) - int(old_heard_depart["n_physical_read_operation"]) if int(
                heard_depart["n_physical_read_operation"]) - int(
                old_heard_depart["n_physical_read_operation"]) > 0 else 0)
        depart_heard_depart["n_sql"] = str(
            int(heard_depart["n_sql"]) - int(old_heard_depart["n_sql"]) if int(heard_depart["n_sql"]) - int(
                old_heard_depart["n_sql"]) > 0 else 0)
        depart_heard_depart["n_shared_blocks_dirtied"] = str(
            int(heard_depart["n_shared_blocks_dirtied"]) - int(old_heard_depart["n_shared_blocks_dirtied"]) if int(
                heard_depart["n_shared_blocks_dirtied"]) - int(old_heard_depart["n_shared_blocks_dirtied"]) > 0 else 0)
        depart_heard_depart["n_table_scan"] = str(
            int(heard_depart["n_table_scan"]) - int(old_heard_depart["n_table_scan"]) if int(
                heard_depart["n_table_scan"]) - int(old_heard_depart["n_table_scan"]) > 0 else 0)
        depart_heard_depart["n_cu_hdd_asyn_read"] = str(
            int(heard_depart["n_cu_hdd_asyn_read"]) - int(old_heard_depart["n_cu_hdd_asyn_read"]) if int(
                heard_depart["n_cu_hdd_asyn_read"]) - int(old_heard_depart["n_cu_hdd_asyn_read"]) > 0 else 0)
        depart_heard_depart["n_local_blocks_dirtied"] = str(
            int(heard_depart["n_local_blocks_dirtied"]) - int(old_heard_depart["n_local_blocks_dirtied"]) if int(
                heard_depart["n_local_blocks_dirtied"]) - int(old_heard_depart["n_local_blocks_dirtied"]) > 0 else 0)
        depart_heard_depart["n_shared_blocks_read"] = str(
            int(heard_depart["n_shared_blocks_read"]) - int(old_heard_depart["n_shared_blocks_read"]) if int(
                heard_depart["n_shared_blocks_read"]) - int(old_heard_depart["n_shared_blocks_read"]) > 0 else 0)
        depart_heard_depart["n_local_blocks_read"] = str(
            int(heard_depart["n_local_blocks_read"]) - int(old_heard_depart["n_local_blocks_read"]) if int(
                heard_depart["n_local_blocks_read"]) - int(old_heard_depart["n_local_blocks_read"]) > 0 else 0)
        depart_heard_depart["n_blocks_read_time"] = str(
            int(heard_depart["n_blocks_read_time"]) - int(old_heard_depart["n_blocks_read_time"]) if int(
                heard_depart["n_blocks_read_time"]) - int(old_heard_depart["n_blocks_read_time"]) > 0 else 0)
        depart_heard_depart["n_blocks_write_time"] = str(
            int(heard_depart["n_blocks_write_time"]) - int(old_heard_depart["n_blocks_write_time"]) if int(
                heard_depart["n_blocks_write_time"]) - int(old_heard_depart["n_blocks_write_time"]) > 0 else 0)
        depart_heard_depart["n_sort_in_memory"] = str(
            int(heard_depart["n_sort_in_memory"]) - int(old_heard_depart["n_sort_in_memory"]) if int(
                heard_depart["n_sort_in_memory"]) - int(old_heard_depart["n_sort_in_memory"]) > 0 else 0)
        depart_heard_depart["n_sort_in_disk"] = str(
            int(heard_depart["n_sort_in_disk"]) - int(old_heard_depart["n_sort_in_disk"]) if int(
                heard_depart["n_sort_in_disk"]) - int(old_heard_depart["n_sort_in_disk"]) > 0 else 0)
        depart_heard_depart["n_cu_mem_hit"] = str(
            int(heard_depart["n_cu_mem_hit"]) - int(old_heard_depart["n_cu_mem_hit"]) if int(
                heard_depart["n_cu_mem_hit"]) - int(old_heard_depart["n_cu_mem_hit"]) > 0 else 0)
        depart_heard_depart["n_cu_hdd_sync_read"] = str(
            int(heard_depart["n_cu_hdd_sync_read"]) - int(old_heard_depart["n_cu_hdd_sync_read"]) if int(
                heard_depart["n_cu_hdd_sync_read"]) - int(old_heard_depart["n_cu_hdd_sync_read"]) > 0 else 0)
        return depart_depart, depart_heard_depart


def computation_time(timestamp):
    """
    computer time generates fixed format
    :param timestamp: get the time in the database
    :return: fixed format time
    """
    timestamp = float(timestamp)
    res_time = ""
    if timestamp == 0:
        res_time = "0h0m0s"
    else:
        res_time += f"{str(int(timestamp//3600000))}h"
        if timestamp % 3600000:
            res_time += f"{str(int(timestamp%3600000//60000))}m"
        if timestamp % 3600000 % 60000:
            num = timestamp % 3600000 % 60000 // 1000
            if timestamp % 3600000 % 60000 % 1000:
                num += 1
            res_time += f"{str(int(num))}s"
    return res_time
