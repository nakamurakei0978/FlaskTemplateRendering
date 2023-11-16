<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Circle Random Color</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>
        body {
            padding: 0;
            margin: 0;
        }

        .main {
            display: grid;
            place-items: center;
            height: 100vh;
        }

        .container {
            height: 600px;
            width: 500px;
            display: grid;
        }

        .container > .circle {
            width: 500px;
            height: 500px;
            border-radius: 50%;
            place-items: center;
            display: grid;
            font-size: 200px;
        }
    </style>
</head>
<body>
<script type="importmap">
  {
    "imports": {
      "vue": "/../../static/js/vue.esm-browser.min.js"
    }
  }
</script>


<div id="app" class="main">
    <div class="container">
        <div :class="'circle bg-'+color" v-text="msg"></div>
        <div class="d-flex justify-content-center gap-2">
            <button :class="'btn btn-'+color" @click="changeColor">Click to change color</button>
            <button :class="'btn btn-'+color" @click="toggleColorRandom" v-text="btn+' random color'"></button>
        </div>
    </div>
</div>


<script type="module">
    // import {createApp, ref} from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
    import {createApp, ref} from 'vue'

    createApp({
        setup() {
            const msg = ref('Hello')
            const color = ref('primary')

            let index = 1
            const colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark', 'link'];

            const changeColor = () => {
                color.value = colors[index];
                index = (index + 1) % colors.length;
            }


            let btn = ref('Start')
            let intervalId = null;
            const randomColor = () => {
                let i = Math.floor(Math.random() * colors.length)
                color.value = colors[i]
            }

            const toggleColorRandom = () => {
                if (btn.value === 'Stop') {
                    btn.value = 'Start'
                    clearInterval(intervalId)
                    intervalId = null
                } else if (btn.value === 'Start') {
                    btn.value = 'Stop'
                    intervalId = setInterval(randomColor, 500) // Change color every millisecond
                }
            }

            return {
                msg, color, changeColor, toggleColorRandom, btn
            }
        }
    }).mount('#app')
</script>
</body>
</html>