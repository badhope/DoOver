<template>
  <div class="interaction-page">
    <div class="page-shell">
      <section class="lane lane-left">
        <header class="lane-head">
          <div class="lane-heading">
            <div class="lane-kicker">Flow</div>
            <h2 class="lane-title">节点</h2>
          </div>
          <span class="status-pill" :class="{ online: isConnected }">
            {{ isConnected ? "WS 已连接" : "WS 未连接" }}
          </span>
        </header>

        <div class="lane-body node-list">
          <button class="send-btn" @click="sendUserInput(cont)">Send Message</button>

          <div
            ref="nodeScrollEl"
            class="node-scroll"
            @scroll="handleNodeScroll"
          >
            <div v-if="!nodeMessages.length" class="empty-state">
              等待节点开始流转
            </div>

            <div
              v-for="(msg, index) in nodeMessages"
              :key="`${msg}-${index}`"
              class="node-row"
              :class="{
                clickable: isHasMsg(msg),
                active: dialogVisible && selectedMsg === msg,
              }"
              @click="handleNodeClick(msg)"
            >
              <NodeComponent
                :isLoading="index == nodeMessages.length - 1"
                :isMsg="isHasMsg(msg)"
                :meta="msg"
                :text="nodeNameToReadable(msg)"
                description="正在处理中..."
              />
            </div>
          </div>
        </div>
      </section>

      <section class="lane lane-center">
        <div class="lane-body stream-stack">
          <div class="stream-switch" role="tablist" aria-label="流式输出切换">
            <button
              type="button"
              class="stream-tab"
              :class="{
                active: selectedStreamKey === 'background',
                populated: !!backgroundText,
              }"
              @click="selectStream('background')"
            >
              <span class="stream-tab-kicker">Background</span>
              <span class="stream-tab-title">{{ nodeNameToReadable("background_node") }}</span>
            </button>
            <button
              type="button"
              class="stream-tab"
              :class="{
                active: selectedStreamKey === 'continue',
                populated: !!continueText,
              }"
              @click="selectStream('continue')"
            >
              <span class="stream-tab-kicker">Continue</span>
              <span class="stream-tab-title">{{ nodeNameToReadable("continue_next_node") }}</span>
            </button>
          </div>

          <div class="stream-stage">
            <Transition name="card-slide" mode="out-in">
              <section :key="selectedStreamKey" class="stream-section stream-section-single">
                <LetterComponent
                  v-if="selectedStreamMeta.content"
                  :meta="selectedStreamMeta.meta"
                  :text="selectedStreamMeta.title"
                  :content="selectedStreamMeta.content"
                />
                <div v-else class="empty-state empty-state-large">
                  {{ selectedStreamMeta.emptyText }}
                </div>
              </section>
            </Transition>
          </div>
        </div>
      </section>

      <section class="lane lane-right">
        <header class="lane-head">
          <div class="lane-heading">
            <div class="lane-kicker">Roles</div>
            <h2 class="lane-title">角色发言</h2>
          </div>
          <span class="status-pill subtle">{{ roleMessages.length }} 条</span>
        </header>

        <div class="lane-body speech-list">
          <div v-if="!roleMessages.length" class="empty-state">
            暂无角色发言
          </div>

          <div v-for="(item, index) in roleMessages" :key="index" class="speech-row">
            <RoleSpeechComponent :roleName="item.roleName" :speech="item.text" />
          </div>
        </div>
      </section>
    </div>

    <div v-if="dialogVisible" class="dialog-mask" @click.self="closeDialog">
      <div class="dialog-container dialog-single">
        <LetterComponent
          v-if="selectedMsg === 'background_node'"
          :meta="selectedMsg"
          :text="nodeNameToReadable(selectedMsg)"
          :content="backgroundText"
        />
        <LetterComponent
          v-else-if="selectedMsg === 'continue_next_node'"
          :meta="selectedMsg"
          :text="nodeNameToReadable(selectedMsg)"
          :content="continueText"
        />
        <SearchContentComponent
          v-else-if="selectedMsg === 'search_node'"
          :content="searchContent || '暂无搜索结果。'"
        />
        <div v-else class="dialog-fallback">暂无可展示的消息：{{ selectedMsg }}</div>
        <button type="button" class="close-btn" @click="closeDialog">关闭</button>
      </div>
    </div>

    <div v-if="pendingQuestion" class="dialog-mask">
      <div class="dialog-container dialog-center">
        <QaNoteComponent
          v-if="pendingQuestion"
          :meta="pendingQuestion.meta"
          :role="pendingQuestion.role"
          :question="pendingQuestion.question"
          @submit="sendUserAnswer"
        />
      </div>
    </div>

    <div
      v-if="choiceDialogVisible && choiceItems.length"
      class="dialog-mask"
      @click.self="closeDialog"
    >
      <div class="dialog-container dialog-stack">
        <CriticalMomentComponent
          v-for="(item, index) in choiceItems"
          :key="index"
          :title="item.key_moment"
          :leftChoice="item.original_action"
          :rightChoices="[item.alternative_action]"
          @submit="handleChoiceSubmit"
        />
      </div>
    </div>

    <div v-if="pendingRole" class="dialog-mask">
      <div class="dialog-container dialog-center">
        <QaNoteComponent
          v-if="pendingRole"
          :meta="pendingRole.field"
          :role="pendingRole.role_name"
          :question="pendingRole.question"
          @submit="sendRoleReply"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { useDooverWs } from "../composables/useDooverWs";
import NodeComponent from "../components/NodeComponent.vue";
import LetterComponent from "../components/LetterComponent.vue";
import QaNoteComponent from "../components/QaNoteComponent.vue";
import RoleSpeechComponent from "../components/RoleSpeechComponent.vue";
import CriticalMomentComponent from "../components/CriticalMomentComponent.vue";
import SearchContentComponent from "../components/SearchContentComponent.vue";

const dialogVisible = ref(false);
const selectedMsg = ref(null);
const nodeScrollEl = ref(null);
const shouldStickNodeScroll = ref(true);
let nodeScrollFrameId = null;

const handleNodeClick = (msg) => {
  // 只允许点击 isMsg 为 true 的节点弹出
  if (!isHasMsg(msg)) return;
  selectedMsg.value = msg;
  dialogVisible.value = true;
};

const closeDialog = () => {
  dialogVisible.value = false;
  choiceDialogVisible.value = false;
  selectedMsg.value = null;
  pendingQuestion.value = null;
  pendingRole.value = null;
  pendingChoices.value = [];
};

const choiceDialogVisible = ref(false);
const handleChoiceSubmit = (choiceText, index) => {
  sendUserChoice(choiceText, index);
  choiceDialogVisible.value = false;
};
const isHasMsg = (msg) => {
  if (
    msg === "background_node" ||
    msg === "continue_next_node" ||
    msg === "search_node"
  )
    return true;
  return false;
};

//节点名称转可读函数
const nodeNameToReadable = (msg) => {
  const nodeNameMap = {
    login_success_node: "登录成功节点",
    init_world_params: "世界参数初始化节点",
    intake_node: "输入接收节点",
    background_node: "背景信息节点",
    agent_node: "工具决策节点",
    tool_node: "工具执行节点",
    wait_user_node: "等待用户补充节点",
    turn_node: "转折事件生成节点",
    user_choice_node: "用户选择节点",
    create_role_node: "角色创建节点",
    role_node: "角色推演节点",
    analyze_interaction_node: "角色互动分析节点",
    tool_node2: "角色互动工具节点",
    wait_for_interaction_from_analyze: "等待角色互动节点",
    continue_next_node: "继续推理节点",
    tool_node3: "继续推理工具节点",
    wait_for_interaction_from_continue: "继续推理等待互动节点",
    should_continue: "继续判断节点",
    should_wait_for_user: "用户等待判断节点",
    should_wait_for_role_interaction: "角色互动等待判断节点",
    search_node: "搜索节点",
  };
  return nodeNameMap[msg] || msg;
};
const {
  isConnected,
  pendingQuestion,
  pendingRole,
  pendingChoices,
  nodeMessages,
  roleMessages,
  backgroundText,
  continueText,
  searchContent,
  sendUserInput,
  sendUserAnswer,
  sendUserChoice,
  sendRoleReply,
} = useDooverWs();

const choiceItems = computed(() => {
  if (Array.isArray(pendingChoices.value)) return pendingChoices.value;
  if (Array.isArray(pendingChoices.value?.items)) return pendingChoices.value.items;
  return [];
});

const selectedStreamKey = ref("background");

const selectStream = (key) => {
  selectedStreamKey.value = key;
};

const selectedStreamMeta = computed(() => {
  if (selectedStreamKey.value === "continue") {
    return {
      key: "continue",
      meta: "continue_next_node",
      kicker: "Continue",
      title: nodeNameToReadable("continue_next_node"),
      content: continueText.value,
      emptyText: "等待继续推理输出",
    };
  }

  return {
    key: "background",
    meta: "background_node",
    kicker: "Background",
    title: nodeNameToReadable("background_node"),
    content: backgroundText.value,
    emptyText: "等待背景信息流入",
  };
});

const isNearNodeScrollBottom = () => {
  const el = nodeScrollEl.value;
  if (!el) return true;
  return el.scrollHeight - el.scrollTop - el.clientHeight < 24;
};

const scrollNodeListToBottom = () => {
  const el = nodeScrollEl.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
};

const handleNodeScroll = () => {
  if (nodeScrollFrameId !== null) return;
  nodeScrollFrameId = requestAnimationFrame(() => {
    nodeScrollFrameId = null;
    shouldStickNodeScroll.value = isNearNodeScrollBottom();
  });
};

watch(pendingChoices, (r) => {
  if (choiceItems.value.length) {
    choiceDialogVisible.value = true;
  }
});

watch(
  () => nodeMessages.value.length,
  async () => {
    await nextTick();
    if (shouldStickNodeScroll.value) {
      scrollNodeListToBottom();
    }
  }
);

watch(backgroundText, (value, previousValue) => {
  if (value && value !== previousValue) {
    selectedStreamKey.value = "background";
  }
});

watch(continueText, (value, previousValue) => {
  if (value && value !== previousValue) {
    selectedStreamKey.value = "continue";
  }
});

watch(roleMessages, (msgs) => {
  if (msgs.length > 0) {
/*     console.log("Received role messages:", msgs); */
  }
});

onBeforeUnmount(() => {
  if (nodeScrollFrameId !== null) {
    cancelAnimationFrame(nodeScrollFrameId);
    nodeScrollFrameId = null;
  }
});

const cont = '初一的时候，我转学到了隔壁县的小乡镇，和外婆住在一起。外婆总说我很瘦，要多吃一些，可是女孩子就是要瘦一些才好看啊。       新学校是住宿学校，食堂的饭菜虽然比不上我的手艺，但就着同学间的嬉闹声，也能吃下半个馒头。或许是因为我太聪明了，虽然对于功课并没有认真，只是听听课写写作业，成绩却也轻轻松松进了年级前十，还拿到了200块钱奖学金，趁着打折，买了貂蝉的仲夏夜之梦。最好看的角色就要穿上最好看的皮肤。       转学一年来，朋友交了不少，情书竟也收到了不少，有时候漂亮也是一种烦恼。       初二期中考试时，学校为了防止作弊，七八年级在一个考场考试，看了考试桌贴，我的邻座应该是七年级的一个男孩子。小学弟，到时候学姐看看能不能帮帮你吧。       直到考试前5分钟，一个满头湿漉漉的小男孩跑进考场，东张西望了一会儿才找到自己的位置——我的邻座。应该是刚洗完头还没来得及擦就来了，有意思。我从口袋里掏出一大截卫生纸，递到他手边，“擦一下，别感冒了”我笑着说道。他犹豫了一下，还是接过卫生纸，很小声地说了一句谢谢，然后又急急地跑出门去。       等他再回来时，考试铃刚刚响起，第一场考语文，试卷早就摆好放在桌子上，他拿起笔就匆匆开始答题，没有再往其他地方看一眼。我翻了一下我的试卷，知道了这次作文没什么难度，又翻回去，开始写题。       出师不利，第一题成语题，我把“如火如荼”的意思给忘了，多冷门的词语啊。瞥了一眼旁边的小男孩，他正在埋头苦写，先跳过吧，待会说不定就想起来了。后面的题目都很顺利，一直到我给作文画上一个句号，放下笔，看了下墙上的时钟，还剩十几分钟，我还是没能想起这个成语的意思，无聊之际，向旁边的小男孩看去。他作文差不多写到最后一段了，落笔的速度越来越慢，我看了一眼监考老师，他正往后面走去，借此机会，我能看到他的整篇作文。       第一段字迹算不上好看，但是比较工整，越往后面写得越急，甚至有些潦草，他刚刚写完的那两句又比较工整，我心里笑了一下，现在才意识到这个问题吗，有点晚了呀。写完最后一个感叹号后，他放下了笔，眼睛却只盯着自己的作文，像一只兔子一样，不敢乱动。我看监考老师走远，小声问他，“小矮子，如火如荼是什么意思呀”。他听到我的问题后头微微向我转了一点点，语气中带着点颤，“额…本来，就是，教材改版了所以我们没学过这个词”。       期中考试而已，有必要这么紧张嘛，有意思。       “好吧，但还是谢谢你了”。我拿着铅笔，在答题卡上随意涂了一个选项。看到监考老师出去，我看向他的整张答题卡。“你这个字该好好练练”。他没有说话，就是盯着自己的答题卡看，然后拿试卷盖住了答题卡。       英语考试前，我和班长商量好，他把填词的答案递给我，我把完型答案给他，互帮互助。进考场前我看到那个小男孩已经在位置上坐好了，想了想，作弊这事，还是算了。       生物考试是我的强项，半小时我完成了整张试卷，又检查了两遍。邻座的小矮子还在奋笔疾书，我只是略微看了一眼，就发现了几处错误。“喂，没有叶绿体也可以光合作用”。他听到我的声音愣了一下，然后恍然大悟般地用橡皮涂改起来，“大意了大意了。”他小声说着。真是大意了吗，哈哈。“还有这题，这题和这题”。       他不再说话，只是一味的涂改。       当所有考试结束，我收拾完东西准备离场时，想着再逗他一下。“小矮子，好好练字。”看到他再次愣了一下，我满足地拿着书包走出考场。       “你们把这条定义抄500遍！”生物老师面无表情地对我和同桌说道。因为在她讲二十一章《人的生殖和发育》时我和同桌对视一眼，没忍住笑了出来。本来我是不会笑的，我知识量比课本讲的丰富得多，但是看到同桌那一脸你懂的的神情，实在忍不住，500遍啊。       学校好像是知道考试座位安排的不合理，期末考试座位安排虽然还是七八年级混考，但是座位和成绩有关，年级第一旁边坐着的也是年级第一。当我走进考场，看到邻座桌贴上那个似曾相识的名字，我有些意外。我更愿意相信是我记错了名字，也难以相信那个小矮子月考年级第十一。       好吧，1000遍的定义同桌都能一天抄完，好像也没有什么事情是不可能的。考试开始的前几分钟，他坐在了我旁边，好像还在偷偷地笑。       “喂，什么事情这么开心”，我戳了戳他，他还是像之前一样，楞了一下，然后支支吾吾地说没有什么事情。我看他还是这么可爱，又再次刁难起他的字，看着他娇羞的摸样很是满足。       初二下学期，第一节晚自习的课间，我正拿着一个甜筒上楼，在二楼的转角处听到了熟悉的声音，向下看去，那个小男孩和一个朋友正有说有笑的上楼。好啊，和其他人说话声音这么大，和我说话声音就这么小。等到他俩走到楼梯转角处时，我站在他们面前，拦住他们。       “打劫！劫色！”       小男孩像是被吓到，停下脚步，他身边那个男生先乐了，伸手推了他胳膊一把，故意提高声音看着他说：“哟，小墨，学姐劫色呢，你咋不说话？是不敢还是舍不得啊？”听到这话他更加慌乱了，一会儿瞟我手里快化了的甜筒，一会儿又盯着楼梯扶手，半天才能挤出一句结结巴巴的话：“我，你，别开玩笑了… 楼上还有同学…”。       我故意往前凑了半步，看他下意识地往后缩了缩，嘴角忍不住翘起来：“开玩笑？我可没开玩笑。刚才在楼下，你跟他说话声音不是挺大的嘛？怎么见了我就变小哑巴了，嗯？” 我指了指他身边的寸头男生，那男生识趣地摆摆手：“我先撤了，你们聊！”说完就溜上了楼，还不忘回头冲小墨点个赞。       楼梯间只剩我们俩，看着他红透的耳朵，我笑着和他说，你叫一声姐姐我就放你过去。看着他难以启齿的样子，我内心得到极大的满足。       “为什么啊”，他声音还是很小。       “因为我比你高”。       “不就高一点吗”。       “高一毫米也是高”，我戏谑地说道。       他想从侧面逃走，但是我怎么会让他如愿，从右方把他向墙上拦住，只是轻轻一推，真的只是轻轻地推，他就被我推到了墙上。       “你怎么比我还轻的感觉，我都没有用力。”       “那我应该比你轻吧，你多重”，他几乎没有迟疑地接过了我的话。       “我怎么可能比你重，我才72斤”。体重是我最自信的数据。       他听到我说完72斤后，好像偷偷抬起头看了我一下       “不信。”他小声地说。       “那你加我QQ，我现拍一张体重给你”。       我最后还是放过了他，第二节晚自习下课，我把准备好的QQ号递给他的朋友转交给他，我相信他免不了朋友的一顿蛐蛐。       就这样他成了我QQ好友，我也没有食言，加上当天拍了一张体重秤数据给他，并附带一句，你什么时候把练好的字拍给我看看。       我渐渐觉得初三的课程有些不对劲，以前稍微花些功夫就能证出来的三角形，现在我看得有些头大，阅读理解也常常偏离文章主旨，班主任多次说我轻浮，让我把基础好好看看。初三再打基础，我自己都觉得好笑，又不是只有我一个人觉得初三题目难啊，班长之前数学还能考130，现在不也只有120了嘛。我觉得分数降低是正常的，再说了不是还有总复习嘛。       “姐姐，我感觉初二时间不够用，作业太多了写不完啊”。小墨在QQ上和我说道。       初二时间不够用？初二时间不是用不完嘛。       “那你可以把作业带回宿舍写，带个小台灯在被子里写。”我虽然不理解他，但是作为名义上的姐姐，还是要出谋划策的。初二不是随便玩玩就行嘛。       我错了，我错得太离谱了。       一模成绩出来时，班级沉寂了。       第一名学委，堪堪过了二中线。       教室太闷了，我想着下楼透透气，在楼梯口遇到了小墨。看着他手里拿着的零食，往事在我面前一一浮现。       初一时我只是在课上和同桌偷偷下棋，初二时我变得更加放纵了，那会儿宿舍十点熄灯，但我能跟下铺聊天到凌晨，假期作业都是开学后找班长的作业抄，有的老师不查我连抄都不抄。虽然两年来考试的名次几乎不变，但是有多少水分我自己知道。       看着面前的小墨，我有些羞愧。       “你…你现在一定要把基础打好，好好学，不然会后悔的，我现在就后悔了”。我看着他说。他点头，“嗯”。没有再说其他话。我不知道再说什么，又折返回了教室。       一模的成绩很说明问题了，班主任给我们上了两节思想课，然后拿着成绩单，把人一个一个地叫到门口，分析问题。其实我们班人都知道，到这个时候了，班主任不是神仙，他也没有灵丹妙药能让我们起死回生。       小墨问我地生教材还在不在，他说学校地生老师都离职了，现在地生是语文和数学老师在教。我想起自己还不错的地生中考成绩，从旧书堆中翻出那七本教材——本来是八本，考完试丢了一本，朋友们的书大都早就卖了，没卖的也很难在找到。开学我把七本书整整齐齐的交给小墨，但愿能给他一点帮助吧。       二模我堪堪过了去年四中的分数线，如果运气好些…       现实没有如果，假设不会成立，中考放榜，学委超常发挥，距离一中还是差10分，我过了民办的乔金高中分数线，但是我清楚民办高中是什么。       放榜那天，小墨给我发了很多消息，劝我上高中，劝我复读。我的问题，一年能解决吗，我知道不能。我没有回小墨的消息，他也真有意思，当天开了个小号加我，当我不知道是他。       “你是？”       “我是谁不重要，上高中的好处有……”       小墨就像一个小孩，不，他本来就是小孩，天真，幼稚。我有些烦躁，把他的小号删除了。       关上了手机WiFi，不想再收到同学群里的消息，我在想我要不要继续读下去。直到外婆喊我吃饭，我告诉外婆，我没有考上。民办高中对大多数人来说和没考上一样，对我来说也是。外婆向我碗里夹了个鸡蛋，没考上就没考上嘛，没考上也得吃饭，你看你瘦的。       外婆说，村里的那谁，不也没考上，后来去了什么中专，也上了大学。       外婆说，小妮子肯定也能去中专，也能上大学。       外婆说，去了哪都要好好吃饭。       外婆说，先别哭，先吃饭。       ……       我扔掉了桌子上那沓厚厚的情书。       八月底，我拎着行李，走进了职校的大门。       高一时，小墨告诉我，他地生中考54分（满分60），多亏了我的书。我能感觉到小墨对县城高中的距离越来越近，也真心为我这个弟弟开心。小墨说要把书还给我，我想着也用不到了，就让他转交给和他同校的另外两个学妹。小墨你自己把握吧。       小墨中考过了二中线，我也在着手准备高职单招考试了。       高二时，小墨告诉我他被校领导欺负了，班主任的态度让他难受，但是又不能和家长说，有些抑郁。我说你把班主任电话给我，我给你骂他。小墨说没事，他没事。       “有些事不能跟家长说就跟我说，不要什么都自己憋着”。我发消息道。       小墨没有回我。翻看着小墨之前说的话，他好像还是那个幼稚的小孩。       他可以一时幼稚，但不能一直幼稚。       男孩子总要独当一面的。       我把微信名片发了过去，让他加我微信。       然后用小号加他QQ，用闺蜜的身份告诉他，我有对象了，别加我。       小墨到底是幼稚，还是发来了好友申请，我通过了。       接下来两天小墨没给我发消息，我知道他开学了，把他删了。       他总要成长。       -------------------       我顺利通过了高职考试，进了一线城市的职业学院，我按照和外婆的约定，一步一步改变着自己。我也不再是那个72斤的小女孩，我是真的长大了。       大二那年，突然收到一条好友申请，看着头像的风格，有些眼熟，我好奇是谁，就通过了。对面加了好友后一直不说话，我点开转账，括号里的名字最后一个字是墨。       我没有删除，只是对他屏蔽了我的朋友圈。       大三那年，我用李跳跳清除微信好友时，发现不知何时，小墨把我删了。       或许对小墨来说，我不是个好姐姐。';
</script>

<style scoped>
.interaction-page {
  min-height: 100vh;
  padding: 42px 16px 56px;
  box-sizing: border-box;
}

.page-shell {
  max-width: 1920px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 404px minmax(520px, 1fr) 390px;
  gap: 40px;
  align-items: start;
}

.lane {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.lane-left,
.lane-center {
  border-right: 1px solid rgba(60, 48, 30, 0.12);
  padding-right: 28px;
}

.lane-right {
  padding-left: 6px;
}

.lane-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  padding-bottom: 18px;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.1);
}

.lane-head-center {
  margin-bottom: 30px;
}

.lane-heading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lane-kicker,
.stream-kicker {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #b6ab9a;
}

.lane-title,
.stream-title {
  margin: 0;
  color: #3d3529;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.lane-title {
  font-size: 19px;
  font-weight: 600;
  line-height: 1.35;
}

.stream-title {
  writing-mode: horizontal-tb;
  white-space: nowrap;
  word-break: keep-all;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.55;
}

.lane-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.node-list,
.speech-list {
  gap: 18px;
}

.node-list {
  min-height: 0;
}

.node-scroll {
  --visible-node-count: 5;/* 最多展示节点数量 */
  --node-row-height: 158px;
  flex: 1;
  min-height: 0;
  max-height: calc(var(--visible-node-count) * var(--node-row-height));
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  scrollbar-width: thin;
  scrollbar-color: rgba(95, 76, 50, 0.26) transparent;
}

.node-scroll::-webkit-scrollbar {
  width: 6px;
}

.node-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.node-scroll::-webkit-scrollbar-thumb {
  background: rgba(95, 76, 50, 0.22);
  border-radius: 999px;
}

.stream-stack {
  gap: 26px;
}

.stream-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  font-size: 5px;
}

.stream-tab {
  appearance: none;
  min-width: 0;
  border: none;
  border-bottom: 0.5px solid rgba(60, 48, 30, 0.22);
  border-radius: 0;
  background: transparent;
  color: #6f6254;
  padding: 8px 4px 10px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, opacity 0.2s ease;
}

.stream-tab:hover {
  border-bottom-color: rgba(60, 48, 30, 0.34);
}

.stream-tab.active {
  background: transparent;
  border-bottom-color: rgba(95, 76, 50, 0.5);
  color: #3d3529;
}

.stream-tab.populated .stream-tab-kicker::after {
  content: "";
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-left: 8px;
  border-radius: 999px;
  background: #5a7a5e;
  vertical-align: middle;
}

.stream-tab-kicker {
  writing-mode: horizontal-tb;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #b6ab9a;
}

.stream-tab-title {
  display: block;
  width: 100%;
  min-width: 0;
  writing-mode: horizontal-tb;
  white-space: nowrap;
  word-break: keep-all;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  line-height: 1.5;
  font-weight: 600;
  text-align: left;
  color: inherit;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.stream-stage {
  min-height: 0;
  position: relative;
  overflow: hidden;
  isolation: isolate;
  contain: paint;
}

.stream-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.stream-section-single {
  width: 100%;
}

.stream-head {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 12px;
}

.card-slide-enter-active,
.card-slide-leave-active {
  transition:
    transform 0.38s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.24s ease,
    filter 0.24s ease;
  will-change: transform, opacity, filter;
}

.card-slide-enter-from {
  opacity: 0;
  filter: blur(1px);
  transform: translateX(34px) scale(0.988);
}

.card-slide-enter-to {
  opacity: 1;
  filter: blur(0);
  transform: translateX(0) scale(1);
}

.card-slide-leave-from {
  opacity: 1;
  filter: blur(0);
  transform: translateX(0) scale(1);
}

.card-slide-leave-to {
  opacity: 0;
  filter: blur(1px);
  transform: translateX(-28px) scale(0.992);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 12px;
  border: 1px solid rgba(127, 116, 95, 0.18);
  border-radius: 4px;
  color: #7b6b56;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  background: rgba(255, 255, 255, 0.18);
}

.status-pill.online {
  color: #5a7a5e;
  border-color: rgba(90, 122, 94, 0.24);
}

.status-pill.subtle {
  background: transparent;
}

.send-btn {
  align-self: flex-start;
  margin-bottom: 10px;
  border: 1.5px solid #3d3529;
  border-radius: 4px;
  background: transparent;
  color: #3d3529;
  padding: 8px 18px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover {
  background: #3d3529;
  color: #faf6ee;
}

.node-row {
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.node-row.clickable {
  cursor: pointer;
}

.node-row.clickable:hover {
  background: rgba(60, 48, 30, 0.04);
}

.node-row.active {
  background: rgba(60, 48, 30, 0.08);
}

.speech-row {
  padding: 4px 0;
}

.empty-state {
  padding: 30px 24px;
  border: 1px dashed rgba(126, 103, 72, 0.3);
  border-radius: 4px;
  color: #8a7458;
  font-size: 14px;
  line-height: 1.75;
  background: rgba(255, 251, 245, 0.16);
}

.empty-state-large {
  min-height: 290px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.dialog-mask {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.718);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 16px;
  box-sizing: border-box;
}

.dialog-container {
  width: min(1200px, calc(100vw - 32px));
  box-sizing: border-box;
}

.dialog-single {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-center {
  display: flex;
  justify-content: center;
}

.dialog-stack {
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: stretch;
  gap: 24px;
  justify-content: center;
  overflow-x: auto;
  padding: 20px;
  box-sizing: border-box;
}
.dialog-stack > * {
  flex: 0 0 min(380px, 85vw);
}
.dialog-fallback {
  width: min(560px, 100%);
  padding: 24px;
  border: 1px solid rgba(60, 48, 30, 0.08);
  border-radius: 4px;
  background: #fafaf7;
}

.close-btn {
  align-self: center;
  margin-top: 4px;
  min-height: 32px;
  padding: 6px 14px;
  background: rgba(249, 245, 238, 0.96);
  border: 1px solid rgba(60, 48, 30, 0.18);
  border-radius: 3px;
  cursor: pointer;
  color: #6f6254;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    transform 0.15s ease;
}

.close-btn:hover {
  background: #f2e7d8;
  border-color: rgba(60, 48, 30, 0.3);
  color: #3d3529;
}

.close-btn:active {
  transform: translateY(1px);
}

@media (max-width: 1480px) {
  .page-shell {
    grid-template-columns: 368px minmax(440px, 1fr) 340px;
    gap: 32px;
  }

  .lane-left,
  .lane-center {
    padding-right: 22px;
  }

  .stream-switch {
    gap: 12px;
  }
}

@media (max-width: 1180px) {
  .interaction-page {
    padding: 24px 16px 32px;
  }

  .page-shell {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .lane-left,
  .lane-center {
    border-right: none;
    padding-right: 0;
  }

  .lane-right {
    padding-left: 0;
  }

  .lane-head,
  .lane-head-center {
    margin-bottom: 20px;
  }

  .stream-stack {
    gap: 34px;
  }

  .node-scroll {
    --node-row-height: 150px;
    max-height: calc(var(--visible-node-count) * var(--node-row-height));
  }

  .stream-switch {
    grid-template-columns: 1fr;
  }

  .empty-state-large {
    min-height: 220px;
  }
}
</style>
