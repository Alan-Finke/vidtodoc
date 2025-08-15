
import os
import extract_frame

def write_html_file(title, summary, vidfile, result):
    #Writes the content of a document to an HTML file.
    print("Writing HTML file...")

    dir = os.getcwd();


    # Create a new Document
    try:
        with open("output.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Software Configuration Manual</title>
    <!-- Tailwind CSS for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Use the Inter font family */
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">


    <!-- Main Container -->
    <div class="container mx-auto max-w-4xl px-4 py-8 sm:py-12">


        <!-- Header Section -->
        <header class="text-center mb-10">
            <h1 class="text-4xl sm:text-5xl font-bold text-gray-900">""" + title + """</h1>
            <!--<p class="mt-2 text-lg text-gray-600">Your one-stop guide to setting up 'Awesome App'</p>-->
        </header>


        <!-- Summary Section -->
        <section id="summary" class="bg-white p-6 sm:p-8 rounded-xl shadow-md mb-12">
            <h2 class="text-2xl font-bold text-gray-900 border-b-2 border-blue-500 pb-2 mb-4">Summary</h2>
            <p class="text-gray-700 leading-relaxed">""" + summary + """</p>
        </section>


        <!-- Step-by-Step Instructions Section -->
        <section id="instructions">
            <h2 class="text-3xl font-bold text-gray-900 text-center mb-8">Step-by-Step Instructions</h2>""");

            step = 1
            for segment in result["segments"]:
                print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
                # Extract a frame at the start of each segment
                frame = "frame" + str(step) + ".jpg";
                extract_frame.extract_frame(vidfile, dir, segment['start'], frame );

                #Add the text to the document
                #document.add_paragraph(segment['text']) ;

                # Add the frame to the document
                #document.add_picture("frame.jpg", width=Inches(5.00));  # Requires 'docx.shared.Inches'

                f.write("""
                <!-- Step  -->
                <div class="step bg-white p-6 sm:p-8 rounded-xl shadow-md mb-8 flex flex-col items-start gap-4">
                    <!-- Step Text Content -->
                    <div class="w-full">
                        <h3 class="text-xl font-bold text-blue-600 mb-2">Step """ + str(step) + """</h3>
                        <p class="text-gray-700">""" + segment['text'] + """</p>
                    </div>
                    <!-- Step Image -->
                    <div class="w-full mt-4">
                        <img src=" """ + frame + """"
                            alt="Screenshot of opening application settings"
                            class="rounded-lg shadow-sm border border-gray-200 w-full h-auto"
                            onerror="this.onerror=null;this.src='https://placehold.co/600x400/e2e8f0/4a5568?text=Image+Not+Found';">
                    </div>
                </div>""")

                step = step + 1


            f.write("""</section>

                <!-- Footer Section -->
                <footer class="text-center mt-12 pt-6 border-t border-gray-300">
                    <p class="text-gray-600">&copy; 2025 Wex,  Inc. All rights reserved.</p>
                </footer>
            </div>
        </body>
        </html>""")
    
        print(f"HTML file saved as output.html")    
            
    except FileNotFoundError:
        print("Error: The specified file path does not exist.")
    except PermissionError:
        print("Error: You do not have permission to write to this file.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")

'''
    # Add a title
    document.add_heading('Video Summary Document', level=1)

    # Add a paragraph
    document.add_paragraph('This document contains the summary and steps extracted from the video.')

    # Save the document as HTML
    html_file_path = os.path.join(os.getcwd(), 'video_summary.html')
    document.save(html_file_path)

    print(f"Document saved as {html_file_path}")
'''

