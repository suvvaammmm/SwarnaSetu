import { useEffect, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";


function App() {

  const [userId, setUserId] = useState("Suvam");
  const [goldPrice, setGoldPrice] = useState(0);
  const [portfolio, setPortfolio] = useState(null);
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [merchantUpi, setMerchantUpi] = useState("");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");


  const chartData = [
  {
    name: "Mon",
    value: 2
  },
  {
    name: "Tue",
    value: 3
  },
  {
    name: "Wed",
    value: 4
  },
  {
    name: "Thu",
    value: 5
  },
  {
    name: "Fri",
    value: portfolio?.portfolio_value || 0
  }
];

  // -----------------------------------------
  // AUTO LOGIN
  // -----------------------------------------

  useEffect(() => {

    const savedUser = localStorage.getItem("user");

    const savedToken = localStorage.getItem("token");

    if (savedUser && savedToken) {

      setUserId(savedUser);

      setIsLoggedIn(true);

    }

  }, []);


  // -----------------------------------------
  // FETCH GOLD PRICE
  // -----------------------------------------

  const fetchGoldPrice = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/gold-price"
      );

      const data = await response.json();

      setGoldPrice(data.price_per_gram);

    } catch (err) {

      console.error(err);

    }
  };


  // -----------------------------------------
  // FETCH BALANCE
  // -----------------------------------------

  const fetchBalance = async () => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/balance/${userId}`
      );

      if (!response.ok) {

        throw new Error("Failed to fetch balance");

      }

      const data = await response.json();

      setBalance(data.balance);

    } catch (err) {

      console.error(err);

      setError("Could not fetch balance");

    }
  };


  // -----------------------------------------
  // FETCH TRANSACTIONS
  // -----------------------------------------

  const fetchTransactions = async () => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/transactions/${userId}`
      );

      if (!response.ok) {

        throw new Error("Failed to fetch transactions");

      }

      const data = await response.json();

      setTransactions(data);

    } catch (err) {

      console.error(err);

      setError("Could not fetch transactions");

    }
  };


  // -----------------------------------------
  // FETCH PORTFOLIO
  // -----------------------------------------

  const fetchPortfolio = async () => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/portfolio/${userId}`
      );

      const data = await response.json();

      setPortfolio(data);

    } catch (err) {

      console.error(err);

    }
  };


  // -----------------------------------------
  // SIGNUP
  // -----------------------------------------

  const signup = async () => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/signup?username=${username}&password=${password}`,
        {
          method: "POST"
        }
      );

      const data = await response.json();

      if (!response.ok) {

        alert(data.detail);

        return;

      }

      alert("Signup Successful");

    } catch (err) {

      console.error(err);

      alert("Signup Failed");

    }
  };


  // -----------------------------------------
  // LOGIN
  // -----------------------------------------

  const login = async () => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/login?username=${username}&password=${password}`,
        {
          method: "POST"
        }
      );

      const data = await response.json();

      if (!response.ok) {

        alert(data.detail);

        return;

      }

      localStorage.setItem(
        "token",
        data.access_token
      );

      localStorage.setItem(
        "user",
        username
      );

      setUserId(username);

      setIsLoggedIn(true);

    } catch (err) {

      console.error(err);

      alert("Login Failed");

    }
  };


  // -----------------------------------------
  // INITIAL LOAD
  // -----------------------------------------

  useEffect(() => {

    if (!userId) return;

    fetchBalance();

    fetchTransactions();

    fetchPortfolio();

    fetchGoldPrice();

  }, [userId]);


  // -----------------------------------------
  // AUTO REFRESH
  // -----------------------------------------

  useEffect(() => {

    if (!userId) return;

    const interval = setInterval(() => {

      fetchBalance();

      fetchTransactions();

      fetchPortfolio();

      fetchGoldPrice();

    }, 3000);

    return () => clearInterval(interval);

  }, [userId]);


  // -----------------------------------------
  // MAKE PAYMENT
  // -----------------------------------------

  const makePayment = async () => {

    try {

      setMessage("");

      setError("");

      const response = await fetch(
        `http://127.0.0.1:8000/pay?user_id=${userId}&merchant_upi=${merchantUpi}&amount=${amount}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {

        throw new Error("Payment failed");

      }

      await response.json();

      setMessage("Payment Successful");

      setMerchantUpi("");

      setAmount("");

      fetchBalance();

      fetchTransactions();

      fetchPortfolio();

    } catch (err) {

      console.error(err);

      setError("Payment Failed");

    }
  };


  // -----------------------------------------
  // LOGIN SCREEN
  // -----------------------------------------

  if (!isLoggedIn) {

    return (

      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">

        <div className="bg-white rounded-2xl shadow-md p-10 w-full max-w-md">

          <h1 className="text-4xl font-bold text-center mb-8">
            SwarnaSetu Auth
          </h1>

          <input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-xl mb-4 outline-none"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-xl mb-6 outline-none"
          />

          <div className="flex gap-4 justify-center">

            <button
              onClick={signup}
              className="bg-black text-white px-6 py-3 rounded-xl hover:opacity-80 transition"
            >
              Signup
            </button>

            <button
              onClick={login}
              className="bg-yellow-500 text-black px-6 py-3 rounded-xl hover:opacity-80 transition"
            >
              Login
            </button>

          </div>

        </div>

      </div>
    );
  }


  // -----------------------------------------
  // DASHBOARD
  // -----------------------------------------

  return (

    <div className="min-h-screen bg-gray-100 p-10 text-black">

      {/* TITLE */}
      <h1 className="text-6xl font-bold text-center mb-8">
        SwarnaSetu Dashboard
      </h1>


      {/* LOGOUT */}
      <button
        onClick={() => {

          localStorage.removeItem("token");

          localStorage.removeItem("user");

          setIsLoggedIn(false);

        }}
        className="bg-black text-white px-5 py-2 rounded-xl hover:opacity-80 transition mb-8"
      >
        Logout
      </button>


      {/* USER INPUT */}
      <div className="flex justify-center mb-10">

        <input
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter User ID"
          className="bg-gray-800 text-white px-4 py-3 rounded-xl w-72 outline-none"
        />

      </div>


      {/* CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6">


        {/* WALLET */}
        <div className="bg-white rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-2xl font-semibold">
            Wallet Balance
          </h2>

          <h1 className="text-5xl font-bold mt-6">
            ₹ {balance}
          </h1>

        </div>


        {/* PORTFOLIO VALUE */}
        <div className="bg-white rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-2xl font-semibold">
            Portfolio Value
          </h2>

          <h1 className="text-5xl font-bold mt-6">
            ₹ {portfolio?.portfolio_value?.toFixed(2)}
          </h1>

        </div>


        {/* GOLD OWNED */}
        <div className="bg-white rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-2xl font-semibold">
            Gold Owned
          </h2>

          <h1 className="text-4xl font-bold mt-6 break-words">
            {portfolio?.gold_grams?.toFixed(8)} g
          </h1>

        </div>


        {/* PROFIT LOSS */}
        <div className="bg-white rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-2xl font-semibold">
            Profit / Loss
          </h2>

          <h1
            className={`text-5xl font-bold mt-6 ${
              portfolio?.profit_loss >= 0
                ? "text-green-600"
                : "text-red-600"
            }`}
          >
            ₹ {portfolio?.profit_loss?.toFixed(2)}
          </h1>

        </div>


        {/* LIVE GOLD PRICE */}
        <div className="bg-yellow-400 rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-2xl font-semibold">
            Live Gold Price
          </h2>

          <h1 className="text-5xl font-bold mt-6">
            ₹ {goldPrice}
          </h1>

          <p className="mt-3 text-lg">
            per gram
          </p>

        </div>

      </div>

      {/* PORTFOLIO ANALYTICS */}
<div className="bg-white rounded-2xl shadow-md p-8 mt-12">

  <h2 className="text-4xl font-bold mb-8">
    Portfolio Analytics
  </h2>

  <div className="w-full h-[400px]">

    <ResponsiveContainer width="100%" height="100%">

      <LineChart data={chartData}>

        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="name" />

        <YAxis />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="value"
          stroke="#f59e0b"
          strokeWidth={4}
        />

      </LineChart>

    </ResponsiveContainer>

  </div>

</div>

      {/* LOWER SECTION */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mt-12">


        {/* PAYMENT CARD */}
        <div className="bg-white rounded-2xl shadow-md p-8 hover:shadow-xl transition">

          <h2 className="text-3xl font-bold text-center mb-8">
            Make Payment
          </h2>


          <input
            type="text"
            placeholder="Merchant UPI"
            value={merchantUpi}
            onChange={(e) => setMerchantUpi(e.target.value)}
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-xl mb-4 outline-none"
          />


          <input
            type="number"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-xl mb-6 outline-none"
          />


          <div className="flex justify-center">

            <button
              onClick={makePayment}
              className="bg-black text-white px-8 py-3 rounded-xl hover:opacity-80 transition"
            >
              Pay
            </button>

          </div>


          {message && (
            <p className="text-green-600 text-center mt-4">
              {message}
            </p>
          )}


          {error && (
            <p className="text-red-600 text-center mt-4">
              {error}
            </p>
          )}

        </div>


        {/* TRANSACTIONS */}
        <div className="xl:col-span-2">

          <h2 className="text-4xl font-bold text-center mb-10">
            Recent Transactions
          </h2>


          {transactions.length === 0 ? (

            <p className="text-center text-gray-500">
              No transactions found
            </p>

          ) : (

            <div className="space-y-5">

              {transactions.map((tx, index) => (

                <div
                  key={index}
                  className="bg-white rounded-2xl shadow-md p-6 hover:shadow-xl transition"
                >

                  <p className="text-lg">
                    Merchant: {tx.merchant_upi}
                  </p>

                  <p className="mt-2">
                    Paid: ₹ {tx.original_amount}
                  </p>

                  <p className="mt-2 text-green-600 font-semibold">
                    Invested Spare Change: ₹ {tx.spare_change}
                  </p>

                  <p className="mt-2 text-gray-500">
                    Status: {tx.status}
                  </p>

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </div>
  );
}

export default App;