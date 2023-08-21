document.addEventListener("DOMContentLoaded", function () {
  // Function to handle the nav link click event
  $(".nav-link").click(function (event) {
    // ... (existing code for handling nav link clicks) ...
  });

  // Check if the current page URL path is for the "Activity" page
  const path = window.location.pathname;

  // Add the 'active' class to the nav link whose URL matches the current page URL
  $(".nav-link").each(function() {
    if ($(this).attr("href") === path) {
      $(this).addClass("active");
    }
  });

  // Manually add the 'active' class to the "Home" nav link if the user is on the home page
  if (path === '/') {
    $(".nav-link.home").addClass("active");
  }

  // Handling category buttons for product filtering
  $(".category-btn").click(function(event) {
    // Prevent the default link behavior
    event.preventDefault();

    // Remove the 'active' class from all category buttons
    $(".category-btn").removeClass("active");

    // Add the 'active' class to the clicked category button
    $(this).addClass("active");

    // Get the data-category attribute value of button that was clicked
    var selectedCategory = $(this).data("category");

    // Show/hide the product cards based on the selected category
    if (selectedCategory === "all") {
       // Show all cards if 'All' is selected
      $(".product-card").removeClass("hidden");
    } else {
      $(".product-card").each(function() {
        // Hide cards with different category than the one selected
        if ($(this).data("category") !== selectedCategory) {
          $(this).addClass("hidden");
        } else {
          $(this).removeClass("hidden");
        }
      });
    }
  });

  // Handle the error messages close button
  $(".btn-dismiss").on("click", function () {
    $(this).closest(".alert").fadeOut();
  });
});
