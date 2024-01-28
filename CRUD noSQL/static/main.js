document.getElementById('card_content').addEventListener('click', function() {
    // Get the contents of the card and pass them to a new page
    var cardContents = document.getElementById('card_content').innerHTML;
    window.location.href = 'newpage.html?contents=' + encodeURIComponent(cardContents);
  });