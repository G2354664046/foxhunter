import { defineStore } from 'pinia'

export const useSampleStore = defineStore('sample', {
  state: () => ({
    samples: [],
    currentSample: null
  }),

  actions: {
    addSample(sample) {
      this.samples.push(sample)
    },

    setCurrentSample(sample) {
      this.currentSample = sample
    },

    updateSample(sampleId, updates) {
      const index = this.samples.findIndex(s => s.id === sampleId)
      if (index !== -1) {
        this.samples[index] = { ...this.samples[index], ...updates }
      }
    }
  }
})