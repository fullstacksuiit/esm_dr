new Vue({
  el: "#purchase",
  data() {
    return {
      purchase_form: [{ name: "", quantity: "", rate: 0, amount: 0 }],
      supplier_id: "",
      supplier_name: "",
      base_url: window.location.origin,
    };
  },
  methods: {
    addSaleRow() {
      data = { name: "", quantity: "", rate: 0, amount: 0 };
      this.purchase_form.push(data);
    },
    removeSaleRow(index) {
      this.purchase_form.splice(index, 1);
    },
    get_supplier() {
      var url = this.base_url + "/purchase/supplier?id=" + this.supplier_id;
      axios
        .get(url)
        .then((response) => {
          this.supplier_name = response.data.name;
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
});
