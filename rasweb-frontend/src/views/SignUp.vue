<template>
  <div>
    <v-img class="bg" src="@/assets/images/bg.jpg">
      <v-container class="container">
        <v-row class="row-form">
          <v-col class="signup-form pl-10 pr-10 pb-5" sm="12" md="6">
            <v-row>
              <v-img
                max-height="70"
                max-width="70"
                src="@/assets/logo/LogoSir.svg"
              ></v-img>
              <h1 class="mt-3">RAS-UAO</h1>
            </v-row>

            <social-login> Regístrate </social-login>
            <v-row class="pa-0 mb-0 mr-1">
              <v-col class="pa-2" sm="5"><div class="line"></div></v-col>
              <v-col class="pa-2" sm="2"
                ><h3 style="text-align: center">Ó</h3></v-col
              >
              <v-col class="pa-2" sm="5"><div class="line"></div></v-col>
            </v-row>
            <form style="width: 100%" @submit.prevent="signUpSubmit">
              <v-row class="mb-0">
                <v-col class="mb-0 pb-0" xs="6">
                  <v-text-field
                    class="mb-1 mt-0 pt-0"
                    v-model="firstName"
                    label="Nombres"
                    :rules="[rules.required]"
                    required
                  ></v-text-field>
                </v-col>
                <v-col class="mb-0 pb-0" sm="6">
                  <v-text-field
                    required
                    class="mb-1 mt-0 pt-0"
                    v-model="lastName"
                    label="Apellidos"
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-text-field
                required
                class="mb-1 pa-0 mt-0"
                v-model="username"
                label="Usuario"
                :rules="[rules.required, rules.valid]"
              ></v-text-field>
              <v-text-field
                required
                class="mb-1 pt-0"
                type="email"
                v-model="email"
                label="Correo"
                :rules="[rules.required]"
              ></v-text-field>
              <v-row class="pt-3">
                <v-col class="mt-0 pt-0" sm="6">
                  <v-text-field
                    required
                    class="mb-1 mt-0 pt-0"
                    v-model="password1"
                    label="Contraseña"
                    :type="view1 ? 'text' : 'password'"
                    :rules="[rules.required, passwordStrong]"
                    :append-icon="view1 ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append="view1 = !view1"
                  ></v-text-field>
                </v-col>
                <v-col class="pt-0" sm="6">
                  <v-text-field
                    required
                    class="mb-1 mt-0 pt-0"
                    v-model="password2"
                    label="Repita la contraseña"
                    :type="view2 ? 'text' : 'password'"
                    :rules="[rules.required, passwordsMatching]"
                    :append-icon="view2 ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append="view2 = !view2"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-progress-linear
                v-if="loading"
                color="accent"
                indeterminate
                rounded
                height="6"
              ></v-progress-linear>
              <v-btn
                class="mr-4"
                color="primary"
                :loading="loading"
                block
                type="submit"
              >
                Registrate
              </v-btn>
              <p class="mt-3 mb-0" align="center">
                ¿Ya tienes una cuenta?
                <a @click="go2LoginView">Inicia sesión</a>
              </p>
            </form>
          </v-col>
          <v-col class="image-signup">
            <v-img src="@/assets/images/circuit.png" class="circuit"></v-img>

            <v-img src="@/assets/images/Duckie_logo.png" class="duckie"></v-img>
          </v-col>
        </v-row>
      </v-container>
    </v-img>
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
import SocialLogin from "../components/SocialLogin.vue";

export default {
  name: "Login",
  components: {
    SocialLogin,
  },
  data: () => ({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    password1: "",
    password2: "",
    signUpDialog: false,
    rules: {
      required: (value) => !!value || "Obligatorio",
      valid: (value) =>
        !/^(?=[a-zA-Z0-9._]{4,20}$)(?!.*[_.]{2})[^_.].*[^_.]$/.test(value)
          ? "Nombre de usuario inválido"
          : true,
    },
    view1: false,
    view2: false,
    loading: false,
    valid: false,
    valid2: false,
    apiDir: "/robotarium-api/v1.0/create-user/",
    snackbar: false,
    message: "",
  }),
  computed: {
    ...mapState(["authentication", "domainBase"]),
    passwordStrong() {
      var regex = /^(?=\w*\d)(?=\w*[A-Z])(?=\w*[a-z])\S{8,16}$/;
      if (!regex.test(this.password1)) {
        this.valid2 = false;
        return "Contraseña débil";
      } else {
        this.valid2 = true;
        return true;
      }
    },
    passwordsMatching() {
      if (this.password1 !== this.password2) {
        this.valid = false;
        return "Las contraseñas no coinciden";
      } else {
        this.valid = true;
        return true;
      }
    },
  },
  mounted() {
    if (this.authentication.auth) {
      this.$router.push({ name: "Home" });
    }
  },
  created() {
    document.title = "SignUp · UAO-RAS";
    this.setViewname("SignUp");
  },
  methods: {
    ...mapMutations(["updateAuthcredentials", "setViewname"]),
    go2LoginView() {
      this.$router.push({ name: "Login" });
    },
    signUpSubmit() {
      this.loading = true;
      if (this.valid && this.valid2) {
        let formData = {
          first_name: this.firstName,
          last_name: this.lastName,
          username: this.username,
          email: this.email,
          password: this.password1,
        };
        this.createUser(formData);
      } else {
      }
    },
    createUser(FormData) {
      fetch(this.domainBase + this.apiDir, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(FormData),
      })
        .then((response) => {
          if (response.status != 200) {
            throw new Error();
          } else {
            return response.json();
          }
        })
        .then((response) => {
          let responseObj = {
            access: response.key,
            auth: !!response.key,
          };
          this.updateAuthcredentials(responseObj);
          this.$router.push({ name: "MoreInfo" });
        })
        .catch((e) => {
          this.snackbar = true;
          this.message =
            "Ya existe una cuenta con este correo o nombre de usuario";
        })
        .finally(() => {
          this.signUpDialog = false;
          this.loading = false;
        });
    },
  },
};
</script>

<style scoped>
h1 {
  color: #424242;
}
.bg {
  position: fixed;
  top: 0px;
  left: 0px;
  width: 100vw;
  height: 100vh;
}
.overlay {
  position: fixed;
  top: 0px;
  left: 0px;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.2);
  z-index: 1;
}
.container {
  width: 100vw;
  height: 40px;
  margin: 5% auto;
}
.row-form {
  border-radius: 15px;
}
.google-logo {
  background: white;
  border-radius: 5px;
  width: 35px;
  height: 35px;
  position: absolute;
  left: -15px;
}
.google-button {
  position: relative;
  background: rgba(89, 4, 4, 1);
  background: -moz-linear-gradient(
    left,
    rgba(89, 4, 4, 1) 0%,
    rgba(192, 7, 7, 1) 55%,
    rgba(192, 7, 7, 1) 100%
  );
  background: -webkit-gradient(
    left top,
    right top,
    color-stop(0%, rgba(89, 4, 4, 1)),
    color-stop(55%, rgba(192, 7, 7, 1)),
    color-stop(100%, rgba(192, 7, 7, 1))
  );
  background: -webkit-linear-gradient(
    left,
    rgba(89, 4, 4, 1) 0%,
    rgba(192, 7, 7, 1) 55%,
    rgba(192, 7, 7, 1) 100%
  );
  background: -o-linear-gradient(
    left,
    rgba(89, 4, 4, 1) 0%,
    rgba(192, 7, 7, 1) 55%,
    rgba(192, 7, 7, 1) 100%
  );
  background: -ms-linear-gradient(
    left,
    rgba(89, 4, 4, 1) 0%,
    rgba(192, 7, 7, 1) 55%,
    rgba(192, 7, 7, 1) 100%
  );
  background: linear-gradient(
    to right,
    rgba(89, 4, 4, 1) 0%,
    rgba(192, 7, 7, 1) 55%,
    rgba(192, 7, 7, 1) 100%
  );
  filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#590404', endColorstr='#c00707', GradientType=1 );
}
.line {
  background: rgba(192, 7, 7, 1) 100%;
  margin: 12px 5px;
  width: 100%;
  height: 3px;
  border-radius: 2px;
}
.forgot-password {
  font-size: 10pt;
  -webkit-user-select: none;
  -moz-user-select: none;
  -khtml-user-select: none;
  -ms-user-select: none;
}
.forgot-password:hover {
  text-decoration: underline;
  cursor: pointer;
}
.image-signup {
  background: #be0707;
  border-radius: 0 10px 10px 0;
  position: relative;
}
.signup-form {
  background: white;
  border-radius: 10px 0 0 10px;
}
.circuit {
  position: absolute;
  top: 0px;
  left: 0px;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  opacity: 0.4;
}
.duckie {
  display: block;
  width: 400px;
  height: auto;
  margin: 20% auto;
}
@media (max-width: 960px) {
  .image-signup {
    display: none;
  }
  .signup-form {
    width: 100%;
  }
  .row-form {
    margin: 5px;
  }
}
p,
a {
  font-size: 12pt;
}
a {
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
</style>