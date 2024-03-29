<template>
  <div>
    <v-card class="pa-3 mr-4 mt-3">
      <v-autocomplete
        v-model="robot"
        :items="robots"
        chips
        color="accent"
        label="Selecciona un robot"
        item-text="name"
        item-value="name, available"
        :readonly="showRobotTools"
      >
        <template v-slot:selection="data">
          <v-chip
            v-bind="data.attrs"
            :input-value="data.selected"
            v-if="data.item.available"
          >
            <v-badge
              bottom
              overlap
              dot
              offset-x="13px"
              offset-y="8px"
              :color="data.item.available ? 'green' : 'grey'"
            >
              <v-avatar color="secondary" left>
                <img
                  :src="data.item.photo"
                  :alt="data.item.name"
                  v-if="data.item.photo"
                />
                <span v-else style="color: white; font-size: 8pt">{{
                  data.item.name.slice(0, 1)
                }}</span>
              </v-avatar>
            </v-badge>
            {{ data.item.name }}
          </v-chip>
        </template>
        <template v-slot:item="data">
          <template v-if="typeof data.item !== 'object'">
            <v-list-item-content v-text="data.item"></v-list-item-content>
          </template>
          <template v-else>
            <v-badge
              bottom
              overlap
              dot
              offset-x="0px"
              offset-y="23px"
              :color="data.item.available ? 'green' : 'grey'"
            >
              <v-list-item-avatar
                @click="setRobotInfo(data.item)"
                color="secondary"
              >
                <img
                  :src="data.item.photo"
                  :alt="data.item.name"
                  v-if="data.item.photo"
                />
                <span v-else style="color: white; font-size: 8pt">{{
                  data.item.name.slice(0, 1)
                }}</span>
              </v-list-item-avatar>
            </v-badge>

            <v-list-item-content
              @click="data.item.available ? setRobotInfo(data.item) : ''"
            >
              <v-list-item-title v-html="data.item.name"></v-list-item-title>
              <v-list-item-subtitle
                class="ml-3"
                v-html="data.item.available ? 'Disponible' : ' No disponible'"
              ></v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </template>
      </v-autocomplete>
      <div v-if="robot && robotObj">
        <a
          class="mx-2 link"
          :href="`http://${appDomain}:${getMeta.compose}`"
          target="_blank"
          >Compose</a
        >
        <a
          :href="`http://${appDomain}:${getMeta.portainer}`"
          class="link"
          target="_blank"
          >Portainer</a
        >
      </div>
      <v-card-actions v-if="robot">
        <v-btn
          block
          @click="closeRobotTools"
          :color="showRobotTools ? '' : 'error'"
        >
          {{ showRobotTools ? "" : "Desconectar" }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <div v-if="robot">
      <v-card class="mt-3 mr-4">
        <joistick
          :wsAddress="websocketAddress"
          :robot="robotObj"
        />
      </v-card>
      <v-card class="mt-4 px-3 mr-4 pb-10">
        <robot-image
          :wsAddress="websocketAddress"
          :robot="robotObj"
          v-on:robotView="setRobotImage"
        />
      </v-card>

      <v-card
        elevation="3"
        width="400"
        :height="img ? '260' : '200'"
        id="drag-box"
      >
        <v-skeleton-loader
          v-if="!img"
          class="mx-auto"
          max-width="400"
          min-height="400"
          type="image"
        >
        </v-skeleton-loader>

        <img v-else :src="'data:image/png;base64,' + img" />
      </v-card>
    </div>

    <v-snackbar v-model="snackbar">
      {{ message }}

      <template v-slot:action="{ attrs }">
        <v-btn color="error" text v-bind="attrs" @click="snackbar = false">
          cerrar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template> 

<script>
import { mapState, mapMutations } from "vuex";
import WebSocketLive from "@/components/subcomponents/WebSocketLive.vue";
import Joistick from "../components/Joistick.vue";
import RobotImage from "../components/RobotImage.vue";
export default {
  name: "RobotVideoStream",
  data: () => ({
    robots: [],
    apiDir: "/robotarium-api/v1.0/robot-list/?format=json",
    robot: "",
    robotObj: "",
    imgBox: false,
    robotAvailable: false,
    showRobotTools: false,
    dragEvent: "",
    snackbar: false,
    message: "",
    img: "",
    appDomain: "aprobotica.uao.edu.co",
    rosConnected: false,
  }),
  components: {
    WebSocketLive,
    Joistick,
    RobotImage,
  },
  created() {
    this.getApiInfo();
  },
  mounted() {
    this.$root.$on("ROSconnected", (data) => {
      this.rosConnected = true;
    });
  },
  computed: {
    ...mapState(["domainBase", "authentication"]),
    getMeta: function () {
      try {
        return JSON.parse(this.robotObj.meta);
      } catch (error) {}
    },
    websocketAddress() {
      let protocol = document.location.protocol == "http:" ? "ws://" : "wss://";
      return protocol + this.appDomain + ":" + this.getMeta.websocket;
    },
  },
  methods: {
    ...mapMutations(["setRobotariumInfo"]),
    getApiInfo() {
      fetch(this.domainBase + this.apiDir, {
        method: "GET",
        headers: {
          Authorization: `Token ${this.authentication.accessToken}`,
        },
      })
        .then((response) => {
          if (response.status == 200) {
            return response.json();
          } else {
            throw new Error();
          }
        })
        .then((response) => {
          this.robots = response;
        })
        .catch(() => {}); //Hacer algo al error en respuesta
    },
    setRobotInfo(info) {
      this.robotObj = info;
      this.$root.$emit("robotSelected", !!this.robotObj);
    },
    closeRobotTools() {
      this.$root.$emit("ROSconnected", {
        status: true,
        robot: this.robotObj.name,
      });
      this.robot = "";
      this.showRobotTools = false;
      this.imgBox = false;
      this.img = "";
      this.$root.$emit("robotSelected", false);
    },
    dragElement() {
      var elmnt = document.getElementById("drag-box");
      elmnt.style = "display: block;";
      var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;
      if (document.getElementById(elmnt.id + "header")) {
        // if present, the header is where you move the DIV from:
        document.getElementById(
          elmnt.id + "header"
        ).onmousedown = dragMouseDown;
      } else {
        // otherwise, move the DIV from anywhere inside the DIV:
        elmnt.onmousedown = dragMouseDown;
      }

      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
      }

      function elementDrag(e) {
        var elmntPos = document
          .getElementById("drag-box")
          .getBoundingClientRect();
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:

        elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
      }

      function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
      }
    },
    setRobotImage(data) {
      if (data) this.img = data;
      if (!this.imgBox) {
        this.dragElement();
        this.imgBox = true;
      }
    },
  },
};
</script>

<style scoped>
#drag-box {
  position: fixed;
  bottom: 3%;
  right: 2%;
  max-width: 500px;
  min-width: 200px;
  width: 340px;
  max-height: 400px;
  min-height: 100px;
  height: 260px;
  cursor: pointer;
  border-radius: 10px;
  overflow: hidden;
  z-index: 1000;
  resize: both;
}
#drag-box img {
  height: 100%;
  min-width: 100%;
}
.chip {
  position: absolute;
  z-index: 101;
  right: 5px;
  top: 3px;
}
.link {
  color: rgb(29, 97, 185);
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}
</style>