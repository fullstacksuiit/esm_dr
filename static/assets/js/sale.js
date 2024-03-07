new Vue({
  el: "#sale",
  data() {
    return {
      items: [{ id: "", name: "", quantity: 1, plate: "full" }],
      base_url: window.location.origin,
      current_table: "",
      orders: [],
      active_bill_id: "",
      dishes: [],
    };
  },
  methods: {
    addSaleRow() {
      console.log("Adding Row");
      let item = { id: "", name: "", quantity: 1, plate: "full" };
      this.items.push(item);
    },
    removeSaleRow(index) {
      this.items.splice(index, 1);
    },
    get_dish(index) {
      var id = this.items[index].id;
      var url = this.base_url + "/sale/dish?dish_id=" + id;
      axios
        .get(url)
        .then((response) => {
          console.log(response.data);
          this.items[index].name = response.data.name;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    remove_order(index) {
      var url = this.base_url + "/sale/";
      var payload = { order_id: this.orders[index].id };
      console.log(payload);
      axios.defaults.xsrfCookieName = 'csrftoken'
      axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
      axios
        .delete(url, { data: payload })
        .then((response) => {
          console.log(response.data);
          this.get_bill(this.active_bill_id);
        })
        .catch((error) => {
          console.log(error.response);
        });
    },
    get_bill(bill_id) {
      var url = this.base_url + "/sale/bill?bill_id=" + bill_id;
      axios
        .get(url)
        .then((response) => {
          console.log(response.data);
          this.current_table = response.data.bill_details.table_no;
          this.orders = response.data.orders;
          this.active_bill_id = response.data.bill_details.id;
        })
        .catch((error) => {
          window.location.reload();
        });
    },
    generate_bill() {
      window.location =
        this.base_url + "/sale/bill/form?bill_id=" + this.active_bill_id;
    },
  },
});
