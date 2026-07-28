// HANDLES STYLES DROPDOWN
document.addEventListener("DOMContentLoaded", () => {
  load_styles();
  load_genres();
});

let current_mode = "semantic";

document.querySelectorAll(".mode-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    current_mode = btn.dataset.mode;

    document
      .querySelectorAll(".mode-btn")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

async function load_styles() {
  let res = await fetch("/styles");
  res = await res.json();

  const dropdown = document.getElementById("style_dropdown");

  // Add a default "all styles" option first that applies no filter
  const all_styles_option = document.createElement("option");
  all_styles_option.textContent = "All Styles";
  all_styles_option.value = "";
  dropdown.appendChild(all_styles_option);

  // Add option to the dropdown menu for each style
  // fetched from the fastapi backend
  for (const style of res) {
    const new_option = document.createElement("option");
    new_option.textContent = style.replaceAll("_", " ");
    new_option.value = style;
    dropdown.appendChild(new_option);
  }
}

async function load_genres() {
  let res = await fetch("/genres");
  res = await res.json();

  const dropdown = document.getElementById("genre_dropdown");

  // Add a default "all styles" option first that applies no filter
  const all_genres_option = document.createElement("option");
  all_genres_option.textContent = "All Genres";
  all_genres_option.value = "";
  dropdown.appendChild(all_genres_option);

  // Add option to the dropdown menu for each style
  // fetched from the fastapi backend
  for (const genre of res) {
    const new_option = document.createElement("option");
    new_option.textContent = genre.replaceAll("_", " ");
    new_option.value = genre;
    dropdown.appendChild(new_option);
  }
}

function render_images(results) {
  const image_region = document.getElementById("results");
  image_region.innerHTML = "";

  for (const res of results) {
    const path = res.path.replace("images/", "");

    const card = document.createElement("div");
    card.className = "card";

    const image = document.createElement("img");
    image.src = `/media/${path}`;

    const body = document.createElement("div");
    body.className = "card-body";

    const artist = document.createElement("div");
    artist.className = "card-artist";
    artist.textContent = res.artist.replaceAll("-", " ");

    const style = document.createElement("div");
    style.className = "card-style";
    style.textContent = res.style.replaceAll("_", " ");

    body.appendChild(artist);
    body.appendChild(style);
    card.appendChild(image);
    card.appendChild(body);
    image_region.appendChild(card);
  }
}

// HANDLES SEARCH BUTTON
const searchbutton = document.getElementById("search_button");
searchbutton.addEventListener("click", search_click);

async function search_click() {
  const searchbar = document.getElementById("query");
  const style_dropdown = document.getElementById("style_dropdown");
  const genre_dropdown = document.getElementById("genre_dropdown");

  const query = searchbar.value;
  const style_choice = style_dropdown.value;
  const genre_choice = genre_dropdown.value;

  const params = new URLSearchParams({
    query: query,
    style: style_choice,
    genre: genre_choice,
    mode: current_mode,
  });

  let res = await fetch(`/search?${params}`);
  res = await res.json();

  // Render images
  render_images(res.results);
}
