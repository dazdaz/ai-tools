/**
 * In Google Slides, this Apps Script opens a window where you paste in Markdown which will create multiple slides
 * @OnlyCurrentDoc
 * Limit the script's scope to the current document and the created slides.
 */

// 1. CREATE THE MENU
// This adds a "Markdown to Slides" menu when you open the Google Doc.
function onOpen() {
  DocumentApp.getUi()
    .createMenu('Markdown to Slides')
    .addItem('Convert to Deck', 'createDeckFromMarkdown')
    .addToUi();
}

// 2. MAIN CONVERSION FUNCTION
function createDeckFromMarkdown() {
  const ui = DocumentApp.getUi();
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody().getText();
  
  // Basic validation to ensure there is content
  if (!body || body.trim() === "") {
    ui.alert("The document appears to be empty.");
    return;
  }

  // Create the new Presentation
  const docTitle = doc.getName() || "New Presentation";
  const deck = SlidesApp.create(docTitle + " (Converted)");
  
  // Remove the default blank title slide created with new decks
  const defaultSlides = deck.getSlides();
  if (defaultSlides.length > 0) {
    defaultSlides[0].remove();
  }

  // Parse the text
  const lines = body.split('\n');
  let currentSlide = null;
  let currentBodyPlaceholder = null;

  lines.forEach(function(line) {
    const trimmedLine = line.trim();
    
    if (trimmedLine === "") return; // Skip empty lines

    if (trimmedLine.startsWith('# ')) {
      // --- H1: New Title Slide ---
      currentSlide = deck.appendSlide(SlidesApp.PredefinedLayout.TITLE);
      const titleShape = currentSlide.getPlaceholder(SlidesApp.PlaceholderType.CENTER_TITLE);
      const titleText = trimmedLine.substring(2); // Remove "# "
      titleShape.asShape().getText().setText(titleText);
      
      // Reset body placeholder since Title slides don't have a standard body
      currentBodyPlaceholder = currentSlide.getPlaceholder(SlidesApp.PlaceholderType.SUBTITLE);

    } else if (trimmedLine.startsWith('## ')) {
      // --- H2: New Title & Body Slide ---
      currentSlide = deck.appendSlide(SlidesApp.PredefinedLayout.TITLE_AND_BODY);
      const titleShape = currentSlide.getPlaceholder(SlidesApp.PlaceholderType.TITLE);
      const titleText = trimmedLine.substring(3); // Remove "## "
      titleShape.asShape().getText().setText(titleText);
      
      // Get the body box to add bullets/text later
      currentBodyPlaceholder = currentSlide.getPlaceholder(SlidesApp.PlaceholderType.BODY);

    } else {
      // --- Content (Bullets or Text) ---
      
      // If we have content but no slide yet, create a generic one
      if (!currentSlide) {
        currentSlide = deck.appendSlide(SlidesApp.PredefinedLayout.TITLE_AND_BODY);
        currentSlide.getPlaceholder(SlidesApp.PlaceholderType.TITLE).asShape().getText().setText("Introduction");
        currentBodyPlaceholder = currentSlide.getPlaceholder(SlidesApp.PlaceholderType.BODY);
      }

      // If the current layout doesn't support body text (unexpected), skip
      if (!currentBodyPlaceholder) return;

      const textRange = currentBodyPlaceholder.asShape().getText();
      
      // Check if it is a list item
      if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
        const listText = trimmedLine.substring(2);
        textRange.appendParagraph(listText).getRange().getListStyle().applyListPreset(SlidesApp.ListPreset.DISC_CIRCLE_SQUARE);
      } else {
        // Regular paragraph
        textRange.appendParagraph(trimmedLine).getRange().getListStyle().removeFromList();
      }
    }
  });

  // Output the result to the user
  const url = deck.getUrl();
  const htmlOutput = HtmlService
    .createHtmlOutput(`<p>Success! <a href="${url}" target="_blank">Click here to open your slide deck</a>.</p>`)
    .setWidth(300)
    .setHeight(100);
  
  ui.showModalDialog(htmlOutput, 'Conversion Complete');
}
