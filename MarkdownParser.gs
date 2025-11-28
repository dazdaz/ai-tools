/**
 * Markdown to Google Slides Converter
 * 
 * SETUP INSTRUCTIONS:
 * 1. Open Google Slides and create a new presentation (or open an existing one)
 * 2. Go to Extensions > Apps Script
 * 3. Delete any existing code and paste this entire script
 * 4. Save the project (Ctrl+S or Cmd+S)
 * 5. Close the Apps Script editor
 * 6. Refresh your Google Slides page
 * 7. A new menu "Markdown Importer" will appear in the menu bar
 * 8. Click "Markdown Importer" > "Import Markdown"
 * 9. Paste your markdown content in the dialog and click "Convert"
 * 
 * ALTERNATIVE: Run from Apps Script Editor
 * 1. After pasting the code, click "Run" > "showImportDialog"
 * 2. Authorize the script when prompted
 * 3. Go back to your Slides to see the dialog
 */

// Menu setup - runs when the presentation is opened
function onOpen() {
  const ui = SlidesApp.getUi();
  ui.createMenu('Markdown Importer')
    .addItem('Import Markdown', 'showImportDialog')
    .addItem('Import from URL', 'showUrlDialog')
    .addSeparator()
    .addItem('Help', 'showHelp')
    .addToUi();
}

// Show the import dialog
function showImportDialog() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
      <head>
        <base target="_top">
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          textarea { width: 100%; height: 400px; font-family: monospace; font-size: 12px; }
          button { 
            background-color: #4285f4; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
          }
          button:hover { background-color: #3367d6; }
          .options { margin: 10px 0; }
          label { margin-right: 20px; }
          .status { margin-top: 10px; color: #666; }
        </style>
      </head>
      <body>
        <h3>Paste Markdown Content</h3>
        <textarea id="markdown" placeholder="# Slide Title&#10;&#10;Content goes here..."></textarea>
        <div class="options">
          <label><input type="checkbox" id="clearExisting"> Clear existing slides first</label>
          <label><input type="checkbox" id="useTheme" checked> Apply default theme</label>
        </div>
        <button onclick="convert()">Convert to Slides</button>
        <div id="status" class="status"></div>
        <script>
          function convert() {
            const markdown = document.getElementById('markdown').value;
            const clearExisting = document.getElementById('clearExisting').checked;
            const useTheme = document.getElementById('useTheme').checked;
            document.getElementById('status').innerText = 'Converting...';
            google.script.run
              .withSuccessHandler(function(result) {
                document.getElementById('status').innerText = result;
              })
              .withFailureHandler(function(error) {
                document.getElementById('status').innerText = 'Error: ' + error.message;
              })
              .convertMarkdownToSlides(markdown, clearExisting, useTheme);
          }
        </script>
      </body>
    </html>
  `)
  .setWidth(700)
  .setHeight(600);
  
  SlidesApp.getUi().showModalDialog(html, 'Import Markdown');
}

// Show URL import dialog
function showUrlDialog() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
      <head>
        <base target="_top">
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          input[type="text"] { width: 100%; padding: 10px; font-size: 14px; }
          button { 
            background-color: #4285f4; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
          }
          button:hover { background-color: #3367d6; }
          .status { margin-top: 10px; color: #666; }
        </style>
      </head>
      <body>
        <h3>Enter Markdown File URL</h3>
        <p>Enter the raw URL of a markdown file (e.g., from GitHub raw content)</p>
        <input type="text" id="url" placeholder="https://raw.githubusercontent.com/...">
        <button onclick="importFromUrl()">Import</button>
        <div id="status" class="status"></div>
        <script>
          function importFromUrl() {
            const url = document.getElementById('url').value;
            document.getElementById('status').innerText = 'Fetching and converting...';
            google.script.run
              .withSuccessHandler(function(result) {
                document.getElementById('status').innerText = result;
              })
              .withFailureHandler(function(error) {
                document.getElementById('status').innerText = 'Error: ' + error.message;
              })
              .importFromUrl(url);
          }
        </script>
      </body>
    </html>
  `)
  .setWidth(500)
  .setHeight(250);
  
  SlidesApp.getUi().showModalDialog(html, 'Import from URL');
}

// Show help dialog
function showHelp() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
          code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
          h4 { margin-top: 20px; color: #4285f4; }
        </style>
      </head>
      <body>
        <h3>Markdown to Slides - Help</h3>
        
        <h4>Supported Markdown Syntax</h4>
        <ul>
          <li><code>## Heading</code> or <code>### SLIDE: Title</code> - Creates a new slide</li>
          <li><code>**bold**</code> - Bold text</li>
          <li><code>*italic*</code> - Italic text</li>
          <li><code>\`code\`</code> - Inline code</li>
          <li><code>- item</code> or <code>* item</code> - Bullet points</li>
          <li><code>1. item</code> - Numbered lists</li>
          <li><code>> quote</code> - Block quotes</li>
          <li><code>\`\`\`code block\`\`\`</code> - Code blocks</li>
          <li><code>| table | row |</code> - Tables</li>
          <li><code>---</code> - Horizontal rule (new slide)</li>
        </ul>
        
        <h4>Tips</h4>
        <ul>
          <li>Use <code>## </code> or <code>### </code> headings to start new slides</li>
          <li>Content under a heading becomes the slide body</li>
          <li>Use <code>---</code> to force a new slide without a title</li>
          <li>Speaker notes can be added after <code>**Speaker Notes:**</code></li>
        </ul>
      </body>
    </html>
  `)
  .setWidth(500)
  .setHeight(450);
  
  SlidesApp.getUi().showModalDialog(html, 'Help');
}

// Import markdown from URL
function importFromUrl(url) {
  try {
    const response = UrlFetchApp.fetch(url);
    const markdown = response.getContentText();
    return convertMarkdownToSlides(markdown, false, true);
  } catch (e) {
    throw new Error('Failed to fetch URL: ' + e.message);
  }
}

// Main conversion function
function convertMarkdownToSlides(markdown, clearExisting, useTheme) {
  const presentation = SlidesApp.getActivePresentation();
  
  // Clear existing slides if requested
  if (clearExisting) {
    const slides = presentation.getSlides();
    for (let i = slides.length - 1; i >= 0; i--) {
      slides[i].remove();
    }
  }
  
  // Parse markdown into slides
  const parsedSlides = parseMarkdown(markdown);
  
  // Create slides
  let slideCount = 0;
  for (const slideData of parsedSlides) {
    createSlide(presentation, slideData, useTheme);
    slideCount++;
  }
  
  return `Successfully created ${slideCount} slides!`;
}

// Parse markdown into slide objects
function parseMarkdown(markdown) {
  const slides = [];
  const lines = markdown.split('\n');
  
  let currentSlide = null;
  let inCodeBlock = false;
  let codeBlockContent = [];
  let inTable = false;
  let tableRows = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Handle code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // End code block
        if (currentSlide) {
          currentSlide.content.push({
            type: 'code',
            text: codeBlockContent.join('\n')
          });
        }
        codeBlockContent = [];
        inCodeBlock = false;
      } else {
        // Start code block
        inCodeBlock = true;
      }
      continue;
    }
    
    if (inCodeBlock) {
      codeBlockContent.push(line);
      continue;
    }
    
    // Handle tables
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableRows = [];
      }
      // Skip separator rows
      if (!line.match(/^\|[\s\-:|]+\|$/)) {
        const cells = line.split('|').filter(c => c.trim() !== '');
        tableRows.push(cells.map(c => c.trim()));
      }
      continue;
    } else if (inTable) {
      // End of table
      if (currentSlide && tableRows.length > 0) {
        currentSlide.content.push({
          type: 'table',
          rows: tableRows
        });
      }
      inTable = false;
      tableRows = [];
    }
    
    // New slide indicators
    const slideMatch = line.match(/^#{1,3}\s+(?:SLIDE\s*\d*:?\s*)?(.+)$/i);
    const hrMatch = line.match(/^-{3,}$|^_{3,}$|^\*{3,}$/);
    
    if (slideMatch || hrMatch) {
      // Save previous slide
      if (currentSlide && (currentSlide.title || currentSlide.content.length > 0)) {
        slides.push(currentSlide);
      }
      
      // Start new slide
      currentSlide = {
        title: slideMatch ? slideMatch[1].trim() : '',
        subtitle: '',
        content: [],
        speakerNotes: ''
      };
      continue;
    }
    
    // If no slide exists yet, create one
    if (!currentSlide) {
      currentSlide = {
        title: '',
        subtitle: '',
        content: [],
        speakerNotes: ''
      };
    }
    
    // Handle subtitle (bold text immediately after title)
    if (line.match(/^\*\*[^*]+\*\*$/) && currentSlide.content.length === 0) {
      currentSlide.subtitle = line.replace(/\*\*/g, '').trim();
      continue;
    }
    
    // Handle speaker notes
    if (line.toLowerCase().includes('speaker notes:')) {
      // Collect all following lines until next heading or empty content
      let notes = [];
      i++;
      while (i < lines.length && !lines[i].match(/^#{1,3}\s/) && !lines[i].match(/^-{3,}$/)) {
        if (lines[i].trim()) {
          notes.push(lines[i].replace(/^[-*]\s*/, '').trim());
        }
        i++;
      }
      i--; // Back up one line
      currentSlide.speakerNotes = notes.join('\n');
      continue;
    }
    
    // Handle block quotes
    if (line.trim().startsWith('>')) {
      const quoteText = line.replace(/^>\s*/, '').trim();
      if (quoteText) {
        currentSlide.content.push({
          type: 'quote',
          text: quoteText
        });
      }
      continue;
    }
    
    // Handle bullet points
    if (line.match(/^\s*[-*•]\s+/)) {
      const bulletText = line.replace(/^\s*[-*•]\s+/, '').trim();
      const indent = (line.match(/^\s*/) || [''])[0].length;
      if (bulletText) {
        currentSlide.content.push({
          type: 'bullet',
          text: bulletText,
          indent: Math.floor(indent / 2)
        });
      }
      continue;
    }
    
    // Handle numbered lists
    if (line.match(/^\s*\d+\.\s+/)) {
      const listText = line.replace(/^\s*\d+\.\s+/, '').trim();
      if (listText) {
        currentSlide.content.push({
          type: 'numbered',
          text: listText
        });
      }
      continue;
    }
    
    // Handle regular paragraphs
    const trimmedLine = line.trim();
    if (trimmedLine && !trimmedLine.match(/^[-=]{3,}$/)) {
      currentSlide.content.push({
        type: 'text',
        text: trimmedLine
      });
    }
  }
  
  // Don't forget the last slide
  if (currentSlide && (currentSlide.title || currentSlide.content.length > 0)) {
    slides.push(currentSlide);
  }
  
  return slides;
}

// Create a single slide
function createSlide(presentation, slideData, useTheme) {
  // Choose layout based on content
  let layout;
  if (!slideData.title && slideData.content.length === 0) {
    layout = SlidesApp.PredefinedLayout.BLANK;
  } else if (slideData.title && slideData.content.length === 0) {
    layout = SlidesApp.PredefinedLayout.SECTION_HEADER;
  } else if (slideData.title) {
    layout = SlidesApp.PredefinedLayout.TITLE_AND_BODY;
  } else {
    layout = SlidesApp.PredefinedLayout.BLANK;
  }
  
  const slide = presentation.appendSlide(layout);
  
  // Get page dimensions
  const pageWidth = presentation.getPageWidth();
  const pageHeight = presentation.getPageHeight();
  
  // Add title
  if (slideData.title) {
    const shapes = slide.getShapes();
    let titleShape = null;
    
    // Find title placeholder
    for (const shape of shapes) {
      const placeholderType = shape.getPlaceholderType();
      if (placeholderType === SlidesApp.PlaceholderType.TITLE || 
          placeholderType === SlidesApp.PlaceholderType.CENTERED_TITLE) {
        titleShape = shape;
        break;
      }
    }
    
    if (titleShape) {
      const textRange = titleShape.getText();
      textRange.setText(slideData.title);
      formatText(textRange);
    } else {
      // Create title text box if no placeholder
      const titleBox = slide.insertTextBox(slideData.title, 50, 30, pageWidth - 100, 60);
      const textRange = titleBox.getText();
      textRange.getTextStyle().setFontSize(32).setBold(true);
      formatText(textRange);
    }
  }
  
  // Add subtitle if present
  if (slideData.subtitle) {
    const shapes = slide.getShapes();
    let subtitleShape = null;
    
    for (const shape of shapes) {
      if (shape.getPlaceholderType() === SlidesApp.PlaceholderType.SUBTITLE) {
        subtitleShape = shape;
        break;
      }
    }
    
    if (subtitleShape) {
      subtitleShape.getText().setText(slideData.subtitle);
    }
  }
  
  // Add content
  if (slideData.content.length > 0) {
    const shapes = slide.getShapes();
    let bodyShape = null;
    
    // Find body placeholder
    for (const shape of shapes) {
      if (shape.getPlaceholderType() === SlidesApp.PlaceholderType.BODY) {
        bodyShape = shape;
        break;
      }
    }
    
    // Build content text
    let contentText = '';
    let hasTable = false;
    let tableData = null;
    
    for (const item of slideData.content) {
      if (item.type === 'table') {
        hasTable = true;
        tableData = item.rows;
        continue;
      }
      
      let prefix = '';
      if (item.type === 'bullet') {
        prefix = '  '.repeat(item.indent || 0) + '• ';
      } else if (item.type === 'numbered') {
        prefix = '  ';
      } else if (item.type === 'quote') {
        prefix = '❝ ';
      } else if (item.type === 'code') {
        prefix = '';
      }
      
      contentText += prefix + item.text + '\n';
    }
    
    if (bodyShape && contentText.trim()) {
      const textRange = bodyShape.getText();
      textRange.setText(contentText.trim());
      formatText(textRange);
    } else if (contentText.trim()) {
      // Create text box if no placeholder
      const contentBox = slide.insertTextBox(
        contentText.trim(), 
        50, 
        slideData.title ? 120 : 50, 
        pageWidth - 100, 
        pageHeight - (slideData.title ? 170 : 100)
      );
      const textRange = contentBox.getText();
      textRange.getTextStyle().setFontSize(18);
      formatText(textRange);
    }
    
    // Add table if present
    if (hasTable && tableData) {
      const tableTop = slideData.title ? 200 : 100;
      const tableHeight = Math.min(tableData.length * 40, pageHeight - tableTop - 50);
      const tableWidth = pageWidth - 100;
      
      try {
        const table = slide.insertTable(tableData.length, tableData[0].length);
        table.setLeft(50);
        table.setTop(tableTop);
        
        for (let row = 0; row < tableData.length; row++) {
          for (let col = 0; col < tableData[row].length; col++) {
            const cell = table.getCell(row, col);
            cell.getText().setText(tableData[row][col]);
            if (row === 0) {
              cell.getText().getTextStyle().setBold(true);
            }
          }
        }
      } catch (e) {
        // If table creation fails, add as text
        const tableText = tableData.map(row => row.join(' | ')).join('\n');
        slide.insertTextBox(tableText, 50, tableTop, tableWidth, tableHeight);
      }
    }
  }
  
  // Add speaker notes
  if (slideData.speakerNotes) {
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(slideData.speakerNotes);
  }
  
  return slide;
}

// Format text (handle markdown inline formatting)
function formatText(textRange) {
  const text = textRange.asString();
  
  // Handle bold text **text**
  const boldPattern = /\*\*([^*]+)\*\*/g;
  let match;
  while ((match = boldPattern.exec(text)) !== null) {
    const start = match.index;
    const end = start + match[0].length;
    try {
      textRange.getRange(start, end).getTextStyle().setBold(true);
    } catch (e) {
      // Ignore formatting errors
    }
  }
  
  // Handle italic text *text* (not inside bold)
  const italicPattern = /(?<!\*)\*([^*]+)\*(?!\*)/g;
  while ((match = italicPattern.exec(text)) !== null) {
    const start = match.index;
    const end = start + match[0].length;
    try {
      textRange.getRange(start, end).getTextStyle().setItalic(true);
    } catch (e) {
      // Ignore formatting errors
    }
  }
  
  // Handle inline code `code`
  const codePattern = /`([^`]+)`/g;
  while ((match = codePattern.exec(text)) !== null) {
    const start = match.index;
    const end = start + match[0].length;
    try {
      textRange.getRange(start, end).getTextStyle()
        .setFontFamily('Courier New')
        .setBackgroundColor('#f4f4f4');
    } catch (e) {
      // Ignore formatting errors
    }
  }
}

// Utility: Create sample slides for testing
function createSampleSlides() {
  const sampleMarkdown = `
## Title Slide

**Subtitle goes here**

---

## Introduction

- First bullet point
- Second bullet point
- Third bullet point

> This is an important quote

---

## Code Example

Here's some code:

\`\`\`javascript
function hello() {
  console.log("Hello, World!");
}
\`\`\`

---

## Table Example

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

---

## Conclusion

**Key Takeaways:**
- Point one
- Point two
- Point three

**Speaker Notes:**
- Remember to pause here
- Make eye contact with the audience
`;

  return convertMarkdownToSlides(sampleMarkdown, false, true);
}
