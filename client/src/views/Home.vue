<template>
    <div class="container">
        <div class="row">
            <div class="col-6">
                <b-card class="mt-3" header="كل الجمل">
                    <table class="table table-responsive-sm">
                        <thead>
                        <tr>
                            <th>الجملة</th>
                            <th>التصنيف</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="doc in docs" :key="doc.id">
                            <td>{{ doc.ar }}</td>
                            <td>{{ doc.cat }}</td>
                        </tr>
                        </tbody>
                    </table>
                </b-card>
            </div>
            <div class="col-6">
                <b-card class="mt-3" header="اصاقة جملة">
                    <b-form @submit="onSubmit" @reset="onReset" v-if="show">
                        <b-form-group
                                label="الجملة"
                                label-for="doc"
                                description="الجملة التي تود اضافتها"
                        >
                            <b-form-input
                                    id="doc"
                                    v-model="form.doc"
                                    type="text"
                                    required
                                    @input="compare"
                                    placeholder="جملة"
                            ></b-form-input>
                        </b-form-group>

                        <b-form-group label="التصنيف" label-for="cat">
                            <b-form-select
                                    id="cat"
                                    v-model="form.cat"
                                    required
                                    :options="options"
                            ></b-form-select>
                        </b-form-group>

                        <b-button type="submit" variant="primary">Submit</b-button>
                        <b-button type="reset" variant="danger">Reset</b-button>
                    </b-form>
                    <b-card class="mt-3" header="التشابه">
                        <table class="table table-responsive-sm">
                            <thead>
                            <tr>
                                <th>الجملة</th>
                                <th>التصنيف</th>
                                <th>تسبة التشابه</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="doc in sims" :key="doc.id">
                                <td>{{ doc.match_sentence.ar }}</td>
                                <td>{{ doc.match_sentence.cat }}</td>
                                <td>{{ doc.score | percent }}</td>
                            </tr>
                            </tbody>
                        </table>
                    </b-card>
                </b-card>
            </div>
        </div>
    </div>
</template>

<script>

import * as axios from 'axios'

export default {
  name: 'home',
  data () {
    return {
      form: {
        doc: '',
        cat: null,
      },
      docs: [],
      sims: [],
      show: true,
      options: [
        {
          text: 'التصنيف',
          value: null
        },
        'رحلات',
        'تخطيط',
        'اسئلة',
      ],
    }
  },
  methods: {
    onSubmit (evt) {
      evt.preventDefault()
      axios.get('http://127.0.0.1:5002/add?text=' + this.form.doc  + '&cat=' + this.form.cat, {
        headers: {
          'Access-Control-Allow-Origin': '*',
        }
      }).then(() => {
        this.getAll()
        this.onReset()
      })
    },
    onReset (evt) {
      evt.preventDefault()
      // Reset our form values
      this.form.doc = ''
      this.form.cat = null
      // Trick to reset/clear native browser form validation state
      this.show = false
      this.$nextTick(() => {
        this.show = true
      })
    },
    getAll () {
      axios.get('http://127.0.0.1:5002/all', {
        headers: {
          'Access-Control-Allow-Origin': '*',
        }
      }).then((res) => {
        this.docs = res.data
      })
    },

    compare () {
      axios.get('http://127.0.0.1:5002/sim?text=' + this.form.doc  + '&cat=' + this.form.cat, {
        headers: {
          'Access-Control-Allow-Origin': '*',
        }
      }).then((res) => {
        if(res.data.result.length > 0) {
          this.sims = res.data.result.filter(d => d.score > 0)
        }
        console.log(this.sims)
      })
    }
  },
  filters: {
    percent(n) {
      return (n * 100).toFixed(2);
    }
  },
  created () {
    this.getAll()
  }
}
</script>
