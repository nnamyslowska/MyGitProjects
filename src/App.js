import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Dashboard from "./Dashboard";
import MyMovies from "./MyMovies";

const App = () => {
  const [favorites, setFavorites] = useState([]);

  const toggleFavorite = (movie) => {
    if (favorites.includes(movie)) {
      setFavorites(favorites.filter((fav) => fav !== movie));
    } else {
      setFavorites([...favorites, movie]);
    }
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={<Dashboard favorites={favorites} toggleFavorite={toggleFavorite} />}
        />
        <Route
          path="/my-movies"
          element={<MyMovies favorites={favorites} />}
        />
      </Routes>
    </Router>
  );
};

export default App;