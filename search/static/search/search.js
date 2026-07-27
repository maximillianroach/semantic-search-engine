// HANDLES STYLES DROPDOWN
document.addEventListener("DOMContentLoaded", () => {
  load_styles();
  load_genres();
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

  // Clear any past images that were here
  image_region.innerHTML = "";

  for (const res of results) {
    // get features
    const style = res.style;
    const artist = res.artist;
    let path = res.path;
    const genre = res.genre;

    const slash_index = path.indexOf("/");
    path = path.slice(slash_index + 1, path.length);

    // create image box, image, and caption elements
    const image_box = document.createElement("div");
    const image = document.createElement("img");
    const caption = document.createElement("div");

    // configure image and point it to the right path
    image.src = `media/${path}`;
    image.width = 200;

    caption.textContent = `${artist.replaceAll("_", " ")} - ${style.replaceAll("_", " ")}`;

    image_box.appendChild(image);
    image_box.append(caption);
    image_region.appendChild(image_box);
  }
}

// HANDLES SEARCH BUTTON
const searchbutton = document.getElementById("search_button");
searchbutton.addEventListener("click", search_click);

async function search_click() {
  const searchbar = document.getElementById("query");
  const dropdown = document.getElementById("style_dropdown");

  const query = searchbar.value;
  const style_choice = dropdown.value;
  const params = new URLSearchParams({ query: query, style: style_choice });

  let res = await fetch(`/search?${params}`);
  res = await res.json();

  // Render images
  render_images(res.results);
}
