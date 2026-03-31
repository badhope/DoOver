from state import AgentState
from time import time as get_current_time
from loguru import logger
from utils.ip_utils import get_country_by_ip
#初始化世界参数
def init_world_params(state: AgentState) -> AgentState:
    time = get_current_time()
    country = get_country_by_ip()
    state["world_info"] = {
        "time": time,
        "country": country,
    }

    return state