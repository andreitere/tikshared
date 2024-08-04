<template>
  <div class="video-container relative group">
    <video
        ref="videoPlayer"
        class="max-w-full max-h-screen"
        autoplay playsinline
        @timeupdate="updateSeekBar"
        @click="playPause"
    >
      <source :src="videoSrc" type="video/mp4" class="max-h-screen">
      Your browser does not support the video tag.
    </video>
    <div
        class="absolute bottom-2 left-0 right-0 flex flex-col items-center space-y-2 transition-opacity duration-300"
    >
      <input
          type="range"
          id="range"
          min="0"
          :max="duration"
          step="0.1"
          v-model="currentTime"
          @input="seek"
          class=" h-1 cursor-pointer mx-5"
      />
    </div>
    <button @click="toggleMute" class="absolute top-10 right-10 z-9 bg-red-500 pointer">🔕brr</button>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';

defineProps({
  videoSrc: {type: String, required: false},
})

const videoPlayer = ref(null);
const showControls = ref(false);
const currentTime = ref(0);
const duration = ref(0);


const toggleMute = () => {
  videoPlayer.value.muted = !videoPlayer.value.muted
}

const playPause = () => {
  const video = videoPlayer.value;
  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
};

const rewind = () => {
  const video = videoPlayer.value;
  video.currentTime = Math.max(0, video.currentTime - 10);
};

const updateSeekBar = (e) => {
  // console.info(e.video.currentTime)
  currentTime.value = videoPlayer.value.currentTime;
  // console.log(currentTime.value);
};

const seek = (event) => {
  videoPlayer.value.currentTime = event.target.value;
};

onMounted(() => {
  videoPlayer.value.onloadedmetadata = () => {
    duration.value = videoPlayer.value.duration;
  };
});

</script>

<style scoped>
.btn {
  @apply bg-blue-500 text-white py-2 px-4 rounded;
}

.video-container {
  @apply flex flex-col items-center;
}


#range {
  -webkit-appearance: none;
  appearance: none;
  width: 90%;
  //padding: 0 10px;
  cursor: pointer;
  outline: none;
  overflow: hidden;
  border-radius: 16px;
}

#range::-webkit-slider-runnable-track {
  height: 15px;
  background: #ccc;
  border-radius: 16px;
}

#range::-moz-range-track {
  height: 15px;
  background: #ccc;
  border-radius: 16px;
}

#range::-webkit-slider-thumb {
  //-webkit-appearance: none;
  content: "🍆";
  //appearance: none;
  height: 15px;
  width: 15px;
  background-color: #fff;
  border-radius: 50%;
  border: 2px solid #f50;
  box-shadow: -407px 0 0 400px #f50;
}

#range::-moz-range-thumb {
  height: 15px;
  width: 15px;
  background-color: #fff;
  border-radius: 50%;
  border: 1px solid #f50;
  box-shadow: -407px 0 0 400px #f50;
}

</style>
