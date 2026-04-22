# ToDo

## 配置持久化
在模型列表列出的模型中新增一个按钮<template>
  <!-- 最简写法 -->
  <v-icon>mdi-connection</v-icon>
  
  <!-- 或者带主题和尺寸的完整写法 -->
  <v-icon 
    icon="mdi-connection"
    class="v-theme--PurpleTheme"
    size="default"
  ></v-icon>
</template>
<script setup>
// Vuetify 3 需要导入 MDI
import { mdiConnection } from '@mdi/js'
</script> 图标  在后端新增一个test_model的api 点击后进行测试(发送消息)并在前端展示结果同时后端要有logging.info  
1. 新增一个data目录,用于持久化用户数据
2. 当前每个json配置是在对应的目录下,不方便持久化用户数据,
后续将会迁移到data目录下

## 记忆功能

1. 在每次对话结束后,将用户所有信息背景压缩保存到data中,后续每次对话前用户可选是否加入历史会话信息
2. 后续考虑接入向量数据库

## 画图功能

1. 每次对话总结分析阶段生成用户经历的一组四宫格漫画

## 角色语音功能

1. 每次生成的角色的话用tts表达出来

## 爬虫功能

1. 通过爬虫获取特点的网页内容,并将其作为用户背景信息的一部分

## 其他功能

1. skills扩展能力

