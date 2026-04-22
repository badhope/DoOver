import { createRouter, createWebHistory } from "vue-router";
import InteractionPage from "../views/InteractionPage.vue";
import NotFoundPage from "../views/NotFoundPage.vue";
import SettingsPage from "../views/SettingsPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "interaction",
      component: InteractionPage,
    },
    {
      path: "/setting",
      name: "setting",
      component: SettingsPage,
      props: { routeAccount: "" },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundPage,
      props: (route) => ({
        path: route.fullPath,
      }),
    },
  ],
});

export default router;
