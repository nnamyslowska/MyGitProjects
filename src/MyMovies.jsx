import React from "react";

const MyMovies = ({ favorites }) => {
  return (
    <div className="container text-center">
      {/* Heading */}
      <h1 className="text-white fw-bold mb-4">My Movies</h1>

      {/* Movie List */}
      <div className="row justify-content-center">
        {favorites.length > 0 ? (
          favorites.map((movie, index) => (
            <div
              className="col-12 mb-3"
              key={index}
              style={{
                backgroundColor: "#1c1c1c",
                borderRadius: "8px",
                padding: "15px",
              }}
            >
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="text-white fw-bold mb-1">{movie.title}</h5>
                  <p className="text-white-50 mb-0">
                    {movie.genre} • {movie.duration}, {movie.format}
                  </p>
                </div>
                <i
                  className="bi bi-star-fill text-warning"
                  style={{ fontSize: "1.5rem" }}
                ></i>
              </div>
            </div>
          ))
        ) : (
          <p className="text-white">No favorite movies to display.</p>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-4 text-white-50">
        <p>© 2025 CineMatch. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default MyMovies;