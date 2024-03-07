new Vue({
  el: "#sale",
  data() {
    return {
      base_url: window.location.origin,
      cust_name: "CASH",
      contact: 0,
      response_orders: [],
      orders: [],
      order_type: "RESTAURANT",
      total: 0,
      sgst: 0,
      cgst: 0,
      subtotal: 0,
      discount_percent: 0,
      discount: 0,
      net: 0,
      bill_id: 0,
      amount_paid: 0,
      amount_due: 0,
      udhaar: false,
      payment_type: "CASH",
    };
  },
  mounted() {
    console.log("Oh I see, You are peeking. You must be from our tribe <3");
    this.get_bill();
  },
  methods: {
    generate_orders() {
      this.orders = [];
      var l = this.response_orders.length;
      for (let i = 0; i < l; i++) {
        var curr = this.response_orders[i];
        var item = {
          name: curr.dish.name,
          quantity: curr.quantity,
          rate: 0,
          size: curr.size,
          amount: 0,
        };
        if (this.order_type == "RESTAURANT") {
          if (item.size == "full") item.rate = curr.dish.restaurant_full_price;
          if (item.size == "half") item.rate = curr.dish.restaurant_half_price;
        }
        if (this.order_type == "SWIGGY") {
          if (item.size == "full") item.rate = curr.dish.swiggy_full_price;
          if (item.size == "half") item.rate = curr.dish.swiggy_half_price;
        }
        if (this.order_type == "ZOMATO") {
          if (item.size == "full") item.rate = curr.dish.zomato_full_price;
          if (item.size == "half") item.rate = curr.dish.zomato_half_price;
        }
        if (this.order_type == "SMATBEE") {
          if (item.size == "full") item.rate = curr.dish.smatbee_full_price;
          if (item.size == "half") item.rate = curr.dish.smatbee_half_price;
        }
        item.amount = item.rate * item.quantity;
        this.orders.push(item);
      }
      this.payment_change();
      this.calculate_money();
    },
    change_order_type() {
      this.generate_orders();
      this.payment_change();
    },
    calculate_discount_percent() {
      this.discount_percent = (this.discount / this.subtotal) * 100;
      this.calculate_money();
    },
    calculate_money() {
      var orders = this.orders;
      var subtotal = 0.0;
      for (let i = 0; i < orders.length; i++) {
        var item = orders[i];
        subtotal = subtotal + item.amount;
      }
      this.discount = ((subtotal * this.discount_percent) / 100.0).toFixed(2);
      this.subtotal = subtotal;
      this.net = this.subtotal - this.discount;
      this.cgst = parseFloat((0.000 * this.net).toFixed(2));
      this.sgst = parseFloat((0.000 * this.net).toFixed(2));
      if (this.order_type == "ZOMATO") {
        this.cgst = 0.0;
        this.sgst = 0.0;
        this.total = (this.net + this.cgst + this.sgst).toFixed(2);
      } 
      if (this.order_type == "SWIGGY") {
        this.total = Math.round(this.net + this.cgst + this.sgst).toFixed(2);
      }
      if (this.order_type == "RESTAURANT") {
       
        this.total = Math.round(this.net + this.cgst + this.sgst).toFixed(2);
      }
      this.amount_paid = this.total;
      this.calculate_amount_due();
    },
    payment_change() {
      if (this.payment_type == "Non Paid") {
        this.cust_name = this.order_type;
        this.amount_paid = 0;
        this.amount_due = this.total;
      }
    },
    calculate_amount_due() {
      this.udhaar = false;
      this.amount_due = parseFloat(this.total - this.amount_paid).toFixed(2);
      if (this.amount_paid != this.total && this.cust_name == "CASH") {
        this.udhaar = true;
        this.cust_name = "";
        this.contact = "";
      }
    },
    get_bill() {
      var url = this.base_url + "/sale/bill" + window.location.search;
      axios
        .get(url)
        .then((response) => {
          this.response_orders = response.data.orders;
          this.bill_id = response.data.bill_details.id;
          this.generate_orders();
          if (response.data.bill_details.kot_status == false) {
            console.log(response.data.bill_details);
            this.discount = response.data.bill_details.discount;
            this.discount_percent =
              (this.discount / response.data.bill_details.sub_total) * 100;
            this.cust_name = response.data.bill_details.cust_name;
            this.contact = response.data.bill_details.contact;
            this.order_type = response.data.bill_details.order_type;
            this.payment_type = response.data.bill_details.payment_type;
            this.amount_paid =
              response.data.bill_details.amount -
              response.data.bill_details.amount_due;
            console.log(this.amount_paid);
            this.amount_due = response.data.bill_details.amount_due;
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },
    redirect() {
      var udhar_true_condition =
        this.udhaar === true && this.cust_name !== "" && this.contact !== "";
      if (this.udhaar === false || udhar_true_condition === true) {
        window.setTimeout(function () {
          // Move to a new location or you can do something else
          window.location.href = window.location.origin;
        }, 1000);
      }
    },
  },
});