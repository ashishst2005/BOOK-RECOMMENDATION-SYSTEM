"""
data_loader.py
--------------
Handles loading and preprocessing of the GoodReads_100k_books.csv dataset.
Falls back to a built-in sample dataset if the CSV is not found.
"""

import ast
import os
import pandas as pd

# ---------------------------------------------------------------------------
# Fallback sample dataset (~100 well-known books with ISBNs)
# ---------------------------------------------------------------------------
SAMPLE_BOOKS = [
    # ── Fantasy ──
    {"Title": "Harry Potter and the Sorcerer's Stone", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.47, "ISBN": "9780590353427", "Description": "A young boy discovers he is a wizard and attends Hogwarts School of Witchcraft and Wizardry."},
    {"Title": "Harry Potter and the Chamber of Secrets", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.43, "ISBN": "9780439064873", "Description": "Harry Potter's second year at Hogwarts is marked by ominous events as the Chamber of Secrets is opened."},
    {"Title": "Harry Potter and the Prisoner of Azkaban", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.57, "ISBN": "9780439136365", "Description": "Harry Potter learns more about his past as a dangerous prisoner escapes from Azkaban."},
    {"Title": "Harry Potter and the Goblet of Fire", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.56, "ISBN": "9780439139601", "Description": "Harry Potter is mysteriously entered into the Triwizard Tournament and faces deadly challenges."},
    {"Title": "Harry Potter and the Order of the Phoenix", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.50, "ISBN": "9780439358071", "Description": "Harry forms a secret student group to fight against Voldemort's rising power."},
    {"Title": "Harry Potter and the Half-Blood Prince", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.57, "ISBN": "9780439785969", "Description": "Dumbledore prepares Harry for the final battle by exploring Voldemort's past."},
    {"Title": "Harry Potter and the Deathly Hallows", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.62, "ISBN": "9780545010221", "Description": "Harry, Ron, and Hermione set out to destroy Voldemort's Horcruxes in a final quest."},
    {"Title": "The Hobbit", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.28, "ISBN": "9780547928227", "Description": "Bilbo Baggins is swept into an epic quest to reclaim the Lonely Mountain from the dragon Smaug."},
    {"Title": "The Lord of the Rings", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.50, "ISBN": "9780544003415", "Description": "A meek hobbit and eight companions set out on a journey to destroy the One Ring and save Middle-earth."},
    {"Title": "The Fellowship of the Ring", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.36, "ISBN": "9780547928210", "Description": "The first part of Tolkien's epic tale of the One Ring and the fellowship formed to destroy it."},
    {"Title": "A Game of Thrones", "Author": "George R.R. Martin", "Genre": "Fantasy", "Rating": 4.44, "ISBN": "9780553593716", "Description": "Noble families fight for control of the Iron Throne of the Seven Kingdoms of Westeros."},
    {"Title": "A Clash of Kings", "Author": "George R.R. Martin", "Genre": "Fantasy", "Rating": 4.41, "ISBN": "9780553579901", "Description": "The Seven Kingdoms are torn apart as five kings claim the Iron Throne."},
    {"Title": "A Storm of Swords", "Author": "George R.R. Martin", "Genre": "Fantasy", "Rating": 4.54, "ISBN": "9780553573428", "Description": "War continues across Westeros and beyond the Wall as alliances shift and betrayals mount."},
    {"Title": "The Name of the Wind", "Author": "Patrick Rothfuss", "Genre": "Fantasy", "Rating": 4.55, "ISBN": "9780756404741", "Description": "The chronicle of the magically gifted young man who grows to be the most notorious wizard his world has ever seen."},
    {"Title": "Mistborn: The Final Empire", "Author": "Brandon Sanderson", "Genre": "Fantasy", "Rating": 4.46, "ISBN": "9780765311788", "Description": "A world where ash falls from the sky and mists dominate the night has been conquered by a dark lord for a thousand years."},
    {"Title": "The Way of Kings", "Author": "Brandon Sanderson", "Genre": "Fantasy", "Rating": 4.64, "ISBN": "9780765326355", "Description": "An epic fantasy set in the world of Roshar, where highstorms and ancient Shardblades shape civilization."},
    {"Title": "Eragon", "Author": "Christopher Paolini", "Genre": "Fantasy", "Rating": 3.97, "ISBN": "9780375826696", "Description": "A farm boy finds a mysterious stone which turns out to be a dragon egg, changing his destiny forever."},
    {"Title": "The Chronicles of Narnia", "Author": "C.S. Lewis", "Genre": "Fantasy", "Rating": 4.24, "ISBN": "9780066238500", "Description": "Seven high fantasy novels set in the world of Narnia ruled by the great lion Aslan."},
    {"Title": "Percy Jackson and the Lightning Thief", "Author": "Rick Riordan", "Genre": "Fantasy", "Rating": 4.25, "ISBN": "9780786838653", "Description": "Percy Jackson, a troubled twelve-year-old, discovers he is a demigod and embarks on a quest across the United States."},
    {"Title": "The Sea of Monsters", "Author": "Rick Riordan", "Genre": "Fantasy", "Rating": 4.24, "ISBN": "9781423103349", "Description": "Percy Jackson must journey to the Sea of Monsters to save Camp Half-Blood from destruction."},
    {"Title": "American Gods", "Author": "Neil Gaiman", "Genre": "Fantasy", "Rating": 4.11, "ISBN": "9780063081918", "Description": "A recently released convict discovers that gods from every world mythology are living among us, preparing for war."},
    {"Title": "Good Omens", "Author": "Neil Gaiman", "Genre": "Fantasy", "Rating": 4.25, "ISBN": "9780060853983", "Description": "An angel and a demon team up to prevent the apocalypse in this witty comedic fantasy."},
    {"Title": "The Wheel of Time: The Eye of the World", "Author": "Robert Jordan", "Genre": "Fantasy", "Rating": 4.19, "ISBN": "9780812511819", "Description": "Five young villagers are drawn into an ancient struggle between Light and Dark when a mysterious woman arrives."},

    # ── Science Fiction ──
    {"Title": "1984", "Author": "George Orwell", "Genre": "Science Fiction", "Rating": 4.19, "ISBN": "9780451524935", "Description": "A dystopian social science fiction novel set in a totalitarian society called Oceania under constant surveillance."},
    {"Title": "Brave New World", "Author": "Aldous Huxley", "Genre": "Science Fiction", "Rating": 3.99, "ISBN": "9780060850524", "Description": "A futuristic World State where citizens are environmentally engineered into intelligence-based social hierarchy."},
    {"Title": "Fahrenheit 451", "Author": "Ray Bradbury", "Genre": "Science Fiction", "Rating": 3.97, "ISBN": "9781451673319", "Description": "In a future American society where books are outlawed and burned by firemen who enforce ignorance."},
    {"Title": "The Martian", "Author": "Andy Weir", "Genre": "Science Fiction", "Rating": 4.40, "ISBN": "9780553418026", "Description": "An astronaut must survive alone on Mars after being presumed dead and left behind by his crew."},
    {"Title": "Dune", "Author": "Frank Herbert", "Genre": "Science Fiction", "Rating": 4.25, "ISBN": "9780441013593", "Description": "Set in the distant future amidst a feudal interstellar society, a young heir becomes the leader of desert warriors."},
    {"Title": "Ender's Game", "Author": "Orson Scott Card", "Genre": "Science Fiction", "Rating": 4.30, "ISBN": "9780812550702", "Description": "A young prodigy is trained to be Earth's greatest military leader to fight an alien race threatening humanity."},
    {"Title": "The Hitchhiker's Guide to the Galaxy", "Author": "Douglas Adams", "Genre": "Science Fiction", "Rating": 4.22, "ISBN": "9780345391803", "Description": "Moments before Earth is demolished for a hyperspace bypass, Arthur Dent is swept off into space."},
    {"Title": "Foundation", "Author": "Isaac Asimov", "Genre": "Science Fiction", "Rating": 4.17, "ISBN": "9780553293357", "Description": "A mathematician develops psychohistory to predict the fall of the Galactic Empire and preserve knowledge."},
    {"Title": "Neuromancer", "Author": "William Gibson", "Genre": "Science Fiction", "Rating": 3.89, "ISBN": "9780441569595", "Description": "A washed-up hacker is hired for one last job in the sprawling digital underworld of cyberspace."},
    {"Title": "Snow Crash", "Author": "Neal Stephenson", "Genre": "Science Fiction", "Rating": 4.02, "ISBN": "9780553380958", "Description": "A pizza delivery driver and hacker discovers a new drug that affects people in both the virtual and real worlds."},
    {"Title": "The Left Hand of Darkness", "Author": "Ursula K. Le Guin", "Genre": "Science Fiction", "Rating": 4.08, "ISBN": "9780441478125", "Description": "An envoy is sent to a planet where inhabitants can change gender, exploring themes of identity and politics."},
    {"Title": "Slaughterhouse-Five", "Author": "Kurt Vonnegut", "Genre": "Science Fiction", "Rating": 4.09, "ISBN": "9780812988529", "Description": "Billy Pilgrim becomes unstuck in time, experiencing moments of his life out of order including the Dresden bombing."},
    {"Title": "2001: A Space Odyssey", "Author": "Arthur C. Clarke", "Genre": "Science Fiction", "Rating": 4.16, "ISBN": "9780451457998", "Description": "Humanity finds a mysterious artifact on the Moon and sets off on a quest to Jupiter with the sentient computer HAL."},
    {"Title": "Do Androids Dream of Electric Sheep?", "Author": "Philip K. Dick", "Genre": "Science Fiction", "Rating": 4.09, "ISBN": "9780345404473", "Description": "A bounty hunter pursues rogue androids in a post-apocalyptic San Francisco, questioning what it means to be human."},
    {"Title": "Project Hail Mary", "Author": "Andy Weir", "Genre": "Science Fiction", "Rating": 4.52, "ISBN": "9780593135204", "Description": "An astronaut wakes up alone on a spaceship with no memory, tasked with saving Earth from an extinction-level threat."},

    # ── Thriller ──
    {"Title": "The Da Vinci Code", "Author": "Dan Brown", "Genre": "Thriller", "Rating": 3.67, "ISBN": "9780307474278", "Description": "A Harvard professor becomes entangled in secrets of symbols while investigating a murder at the Louvre."},
    {"Title": "Gone Girl", "Author": "Gillian Flynn", "Genre": "Thriller", "Rating": 3.86, "ISBN": "9780307588371", "Description": "On a couple's fifth wedding anniversary, the wife mysteriously disappears and suspicion falls on the husband."},
    {"Title": "The Girl with the Dragon Tattoo", "Author": "Stieg Larsson", "Genre": "Thriller", "Rating": 4.15, "ISBN": "9780307454546", "Description": "A journalist and a brilliant hacker investigate the decades-old disappearance of a woman from a wealthy family."},
    {"Title": "The Girl on the Train", "Author": "Paula Hawkins", "Genre": "Thriller", "Rating": 3.88, "ISBN": "9781594634024", "Description": "A woman who commutes by train becomes entangled in a missing persons investigation that changes her life."},
    {"Title": "The Silent Patient", "Author": "Alex Michaelides", "Genre": "Thriller", "Rating": 4.02, "ISBN": "9781250301697", "Description": "A woman shoots her husband and then never speaks again; a therapist becomes obsessed with uncovering her motive."},
    {"Title": "Angels & Demons", "Author": "Dan Brown", "Genre": "Thriller", "Rating": 3.89, "ISBN": "9781416524793", "Description": "Robert Langdon follows clues left by the Illuminati through Rome in a race against time."},
    {"Title": "Inferno", "Author": "Dan Brown", "Genre": "Thriller", "Rating": 3.60, "ISBN": "9781400079155", "Description": "Robert Langdon wakes up in a hospital with amnesia and must solve a mystery inspired by Dante's Inferno."},
    {"Title": "Before I Go to Sleep", "Author": "S.J. Watson", "Genre": "Thriller", "Rating": 3.78, "ISBN": "9780062060563", "Description": "A woman wakes up every day with no memory and begins to discover that her life is not what she has been told."},

    # ── Mystery ──
    {"Title": "Murder on the Orient Express", "Author": "Agatha Christie", "Genre": "Mystery", "Rating": 4.15, "ISBN": "9780062693662", "Description": "Detective Hercule Poirot investigates a murder on the famous luxury train stranded in a snowdrift."},
    {"Title": "And Then There Were None", "Author": "Agatha Christie", "Genre": "Mystery", "Rating": 4.27, "ISBN": "9780062073488", "Description": "Ten strangers are lured to an isolated island and killed one by one according to a nursery rhyme."},
    {"Title": "The Hound of the Baskervilles", "Author": "Arthur Conan Doyle", "Genre": "Mystery", "Rating": 4.12, "ISBN": "9780451528018", "Description": "Sherlock Holmes investigates the legend of a supernatural hound terrorizing the Baskerville family on the moors."},
    {"Title": "A Study in Scarlet", "Author": "Arthur Conan Doyle", "Genre": "Mystery", "Rating": 4.15, "ISBN": "9780486474007", "Description": "The first Sherlock Holmes novel, introducing the detective and Dr. Watson as they solve a mysterious murder."},
    {"Title": "The Big Sleep", "Author": "Raymond Chandler", "Genre": "Mystery", "Rating": 3.96, "ISBN": "9780394758282", "Description": "Private detective Philip Marlowe is drawn into a complex web of blackmail, murder, and deceit in Los Angeles."},
    {"Title": "In the Woods", "Author": "Tana French", "Genre": "Mystery", "Rating": 3.86, "ISBN": "9780143113492", "Description": "A Dublin detective investigates a child's murder in a case echoing the unsolved disappearance of his childhood friends."},

    # ── Dystopian ──
    {"Title": "The Hunger Games", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.34, "ISBN": "9780439023481", "Description": "In a dystopian future, a young girl takes her sister's place in a televised death match between districts."},
    {"Title": "Catching Fire", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.30, "ISBN": "9780439023498", "Description": "The second book in the Hunger Games trilogy as Katniss becomes a symbol of revolution against the Capitol."},
    {"Title": "Mockingjay", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.03, "ISBN": "9780439023511", "Description": "The final battle against the Capitol begins as Katniss becomes the Mockingjay, leader of the rebellion."},
    {"Title": "Divergent", "Author": "Veronica Roth", "Genre": "Dystopian", "Rating": 4.10, "ISBN": "9780062024039", "Description": "In a dystopian Chicago, society is divided into five factions based on virtues and one girl doesn't fit in."},
    {"Title": "The Maze Runner", "Author": "James Dashner", "Genre": "Dystopian", "Rating": 4.02, "ISBN": "9780385737951", "Description": "A boy arrives in a community of boys trapped in a deadly maze with no memory of the outside world."},
    {"Title": "The Giver", "Author": "Lois Lowry", "Genre": "Dystopian", "Rating": 4.13, "ISBN": "9780544336261", "Description": "In a seemingly perfect society, a boy is chosen to inherit the position of Receiver of Memory and discovers dark truths."},
    {"Title": "The Handmaid's Tale", "Author": "Margaret Atwood", "Genre": "Dystopian", "Rating": 4.11, "ISBN": "9780385490818", "Description": "In a totalitarian theocracy, a woman is forced into reproductive servitude and struggles to survive."},

    # ── Romance ──
    {"Title": "Pride and Prejudice", "Author": "Jane Austen", "Genre": "Romance", "Rating": 4.28, "ISBN": "9780141439518", "Description": "Elizabeth Bennet navigates issues of manners, morality, marriage and love in Georgian England."},
    {"Title": "Sense and Sensibility", "Author": "Jane Austen", "Genre": "Romance", "Rating": 4.08, "ISBN": "9780141439662", "Description": "Two sisters navigate love and heartbreak with contrasting temperaments in Regency-era England."},
    {"Title": "Wuthering Heights", "Author": "Emily Brontë", "Genre": "Romance", "Rating": 3.86, "ISBN": "9780141439556", "Description": "A brooding tale of passionate love and revenge set on the Yorkshire moors spanning two generations."},
    {"Title": "Jane Eyre", "Author": "Charlotte Brontë", "Genre": "Romance", "Rating": 4.13, "ISBN": "9780141441146", "Description": "An orphaned governess falls in love with her employer, only to discover he harbors a dark secret."},
    {"Title": "The Notebook", "Author": "Nicholas Sparks", "Genre": "Romance", "Rating": 4.10, "ISBN": "9781455582877", "Description": "A man reads a love story to a woman suffering from dementia, hoping to spark her memory of their romance."},
    {"Title": "Outlander", "Author": "Diana Gabaldon", "Genre": "Romance", "Rating": 4.25, "ISBN": "9780440212560", "Description": "A World War II nurse is transported back to 18th-century Scotland where she meets a Highland warrior."},
    {"Title": "Me Before You", "Author": "Jojo Moyes", "Genre": "Romance", "Rating": 4.27, "ISBN": "9780143124542", "Description": "A cheerful young woman becomes the caretaker of a paralyzed man, and they form an unexpected bond."},

    # ── Fiction / Literary ──
    {"Title": "The Alchemist", "Author": "Paulo Coelho", "Genre": "Fiction", "Rating": 3.88, "ISBN": "9780062315007", "Description": "A young shepherd journeys to the Egyptian pyramids following a recurring dream about finding treasure."},
    {"Title": "To Kill a Mockingbird", "Author": "Harper Lee", "Genre": "Fiction", "Rating": 4.28, "ISBN": "9780060935467", "Description": "A lawyer in the Deep South defends a Black man accused of a crime, seen through his young daughter's eyes."},
    {"Title": "The Great Gatsby", "Author": "F. Scott Fitzgerald", "Genre": "Fiction", "Rating": 3.93, "ISBN": "9780743273565", "Description": "A portrait of the Jazz Age in all of its decadence and excess, told through the eyes of Nick Carraway."},
    {"Title": "Of Mice and Men", "Author": "John Steinbeck", "Genre": "Fiction", "Rating": 3.88, "ISBN": "9780140186420", "Description": "Two displaced migrant ranch workers move from place to place in Depression-era California."},
    {"Title": "The Catcher in the Rye", "Author": "J.D. Salinger", "Genre": "Fiction", "Rating": 3.80, "ISBN": "9780316769488", "Description": "A disillusioned teenager wanders New York City after being expelled from prep school."},
    {"Title": "One Hundred Years of Solitude", "Author": "Gabriel García Márquez", "Genre": "Fiction", "Rating": 4.10, "ISBN": "9780060883287", "Description": "The multi-generational story of the Buendía family in the mythical town of Macondo."},
    {"Title": "The Kite Runner", "Author": "Khaled Hosseini", "Genre": "Fiction", "Rating": 4.31, "ISBN": "9781594631931", "Description": "A haunting tale of friendship, betrayal, and redemption set against the backdrop of Afghanistan's tumultuous history."},
    {"Title": "Life of Pi", "Author": "Yann Martel", "Genre": "Fiction", "Rating": 3.93, "ISBN": "9780156027328", "Description": "A young man survives 227 days stranded on a lifeboat in the Pacific Ocean with a Bengal tiger."},
    {"Title": "The Book Thief", "Author": "Markus Zusak", "Genre": "Fiction", "Rating": 4.37, "ISBN": "9780375842207", "Description": "Narrated by Death, a girl growing up in Nazi Germany steals books and shares them with neighbors."},
    {"Title": "Beloved", "Author": "Toni Morrison", "Genre": "Fiction", "Rating": 3.88, "ISBN": "9781400033416", "Description": "A formerly enslaved woman is haunted by the ghost of her deceased daughter in post-Civil War Ohio."},

    # ── Horror ──
    {"Title": "Dracula", "Author": "Bram Stoker", "Genre": "Horror", "Rating": 3.98, "ISBN": "9780486411095", "Description": "Count Dracula's attempt to move from Transylvania to England so he can find new blood and spread the undead curse."},
    {"Title": "Frankenstein", "Author": "Mary Shelley", "Genre": "Horror", "Rating": 3.82, "ISBN": "9780486282114", "Description": "A young scientist creates a sapient creature in an unorthodox scientific experiment and faces the consequences."},
    {"Title": "It", "Author": "Stephen King", "Genre": "Horror", "Rating": 4.24, "ISBN": "9781501142970", "Description": "A group of children find themselves battling an evil entity that takes the form of a clown named Pennywise."},
    {"Title": "The Shining", "Author": "Stephen King", "Genre": "Horror", "Rating": 4.22, "ISBN": "9780307743657", "Description": "A family moves into an isolated hotel for the winter where a sinister presence drives the father to madness."},
    {"Title": "Pet Sematary", "Author": "Stephen King", "Genre": "Horror", "Rating": 3.98, "ISBN": "9781501156700", "Description": "A family discovers a mysterious burial ground near their home that has the power to bring the dead back to life."},
    {"Title": "The Exorcist", "Author": "William Peter Blatty", "Genre": "Horror", "Rating": 4.11, "ISBN": "9780061007224", "Description": "A mother seeks help when her daughter begins displaying bizarre and violent behavior that defies medical explanation."},
    {"Title": "House of Leaves", "Author": "Mark Z. Danielewski", "Genre": "Horror", "Rating": 4.10, "ISBN": "9780375703768", "Description": "A family discovers their house is larger on the inside than the outside in this experimental horror novel."},

    # ── Non-Fiction ──
    {"Title": "Sapiens: A Brief History of Humankind", "Author": "Yuval Noah Harari", "Genre": "Non-Fiction", "Rating": 4.40, "ISBN": "9780062316097", "Description": "A brief history of humankind exploring how biology and history have defined us and shaped our societies."},
    {"Title": "Atomic Habits", "Author": "James Clear", "Genre": "Non-Fiction", "Rating": 4.38, "ISBN": "9780735211292", "Description": "A practical guide to building good habits and breaking bad ones using small incremental changes."},
    {"Title": "Thinking, Fast and Slow", "Author": "Daniel Kahneman", "Genre": "Non-Fiction", "Rating": 4.18, "ISBN": "9780374533557", "Description": "Explores the two systems that drive the way we think: fast intuitive thinking and slow deliberate thinking."},
    {"Title": "Educated", "Author": "Tara Westover", "Genre": "Non-Fiction", "Rating": 4.47, "ISBN": "9780399590504", "Description": "A memoir about a young woman who grows up in a survivalist family and goes on to earn a PhD from Cambridge."},
    {"Title": "Becoming", "Author": "Michelle Obama", "Genre": "Non-Fiction", "Rating": 4.39, "ISBN": "9781524763138", "Description": "The former First Lady chronicles her life from childhood on the South Side of Chicago to the White House."},
    {"Title": "A Brief History of Time", "Author": "Stephen Hawking", "Genre": "Non-Fiction", "Rating": 4.21, "ISBN": "9780553380163", "Description": "An accessible exploration of cosmology, black holes, the Big Bang, and the nature of time."},
    {"Title": "The Immortal Life of Henrietta Lacks", "Author": "Rebecca Skloot", "Genre": "Non-Fiction", "Rating": 4.07, "ISBN": "9781400052189", "Description": "The story of Henrietta Lacks, whose cancer cells were taken without consent and became vital to medical research."},

    # ── Self-Help ──
    {"Title": "The Power of Now", "Author": "Eckhart Tolle", "Genre": "Self-Help", "Rating": 4.13, "ISBN": "9781577314806", "Description": "A guide to spiritual enlightenment exploring the importance of living in the present moment."},
    {"Title": "Rich Dad Poor Dad", "Author": "Robert T. Kiyosaki", "Genre": "Self-Help", "Rating": 4.08, "ISBN": "9781612680194", "Description": "What the rich teach their kids about money that the poor and middle class do not."},
    {"Title": "The Subtle Art of Not Giving a F*ck", "Author": "Mark Manson", "Genre": "Self-Help", "Rating": 3.90, "ISBN": "9780062457714", "Description": "A counterintuitive approach to living a good life by choosing what to care about carefully."},
    {"Title": "How to Win Friends and Influence People", "Author": "Dale Carnegie", "Genre": "Self-Help", "Rating": 4.22, "ISBN": "9780671027032", "Description": "Timeless advice on building relationships, winning people over, and becoming more persuasive."},
    {"Title": "The 7 Habits of Highly Effective People", "Author": "Stephen R. Covey", "Genre": "Self-Help", "Rating": 4.11, "ISBN": "9781982137274", "Description": "A principle-centered approach for solving personal and professional problems."},

    # ── Historical Fiction ──
    {"Title": "All the Light We Cannot See", "Author": "Anthony Doerr", "Genre": "Historical Fiction", "Rating": 4.33, "ISBN": "9781501173219", "Description": "A blind French girl and a German boy find their paths colliding in occupied France during World War II."},
    {"Title": "The Pillars of the Earth", "Author": "Ken Follett", "Genre": "Historical Fiction", "Rating": 4.31, "ISBN": "9780451166890", "Description": "A sweeping epic about the building of a cathedral in 12th-century England amid political intrigue."},
    {"Title": "The Shadow of the Wind", "Author": "Carlos Ruiz Zafón", "Genre": "Historical Fiction", "Rating": 4.27, "ISBN": "9780143034902", "Description": "A boy discovers a book by an obscure author and searches Barcelona for the writer's remaining works."},
    {"Title": "Memoirs of a Geisha", "Author": "Arthur Golden", "Genre": "Historical Fiction", "Rating": 4.14, "ISBN": "9780679781585", "Description": "The story of a Japanese girl's journey from a fishing village to becoming one of Kyoto's most celebrated geishas."},
    {"Title": "The Night Circus", "Author": "Erin Morgenstern", "Genre": "Historical Fiction", "Rating": 4.04, "ISBN": "9780307744432", "Description": "Two young magicians are pitted against each other in a mysterious circus that appears without warning."},

    # ── Philosophy ──
    {"Title": "Meditations", "Author": "Marcus Aurelius", "Genre": "Philosophy", "Rating": 4.25, "ISBN": "9780140449334", "Description": "The personal writings of the Roman Emperor on Stoic philosophy, self-discipline, and resilience."},
    {"Title": "The Republic", "Author": "Plato", "Genre": "Philosophy", "Rating": 3.95, "ISBN": "9780140455113", "Description": "Plato's foundational work on justice, the ideal state, and the nature of the human soul."},
    {"Title": "Beyond Good and Evil", "Author": "Friedrich Nietzsche", "Genre": "Philosophy", "Rating": 3.95, "ISBN": "9780140449235", "Description": "Nietzsche challenges conventional morality and explores the will to power and the nature of truth."},
    {"Title": "Man's Search for Meaning", "Author": "Viktor E. Frankl", "Genre": "Philosophy", "Rating": 4.37, "ISBN": "9780807014295", "Description": "A psychiatrist's memoir of surviving the Holocaust and his theory that meaning is the primary motivation in life."},

    # ── Adventure ──
    {"Title": "Treasure Island", "Author": "Robert Louis Stevenson", "Genre": "Adventure", "Rating": 3.83, "ISBN": "9780141321004", "Description": "A young boy sets sail for a remote island to find buried pirate treasure in this classic adventure tale."},
    {"Title": "The Count of Monte Cristo", "Author": "Alexandre Dumas", "Genre": "Adventure", "Rating": 4.27, "ISBN": "9780140449266", "Description": "An innocent man is imprisoned, escapes, and uses a hidden fortune to exact revenge on those who betrayed him."},
    {"Title": "Around the World in Eighty Days", "Author": "Jules Verne", "Genre": "Adventure", "Rating": 3.89, "ISBN": "9780141441108", "Description": "An English gentleman wagers that he can travel around the entire world in just eighty days."},
    {"Title": "Robinson Crusoe", "Author": "Daniel Defoe", "Genre": "Adventure", "Rating": 3.67, "ISBN": "9780141439822", "Description": "A castaway survives twenty-eight years on a remote island, encountering cannibals and mutineers."},

    # ── Classics ──
    {"Title": "Don Quixote", "Author": "Miguel de Cervantes", "Genre": "Classics", "Rating": 3.88, "ISBN": "9780060934347", "Description": "A middle-aged man obsessed with chivalric romances sets out on a series of misadventures as a self-proclaimed knight."},
    {"Title": "Crime and Punishment", "Author": "Fyodor Dostoevsky", "Genre": "Classics", "Rating": 4.22, "ISBN": "9780486415871", "Description": "A poor student commits a murder and is consumed by guilt, paranoia, and a moral crisis."},
    {"Title": "Anna Karenina", "Author": "Leo Tolstoy", "Genre": "Classics", "Rating": 4.05, "ISBN": "9780143035008", "Description": "A married aristocrat begins a passionate affair that leads to her social downfall in Imperial Russia."},
    {"Title": "War and Peace", "Author": "Leo Tolstoy", "Genre": "Classics", "Rating": 4.11, "ISBN": "9781400079988", "Description": "An epic tale of Russian society during the Napoleonic Wars, following several aristocratic families."},
    {"Title": "The Brothers Karamazov", "Author": "Fyodor Dostoevsky", "Genre": "Classics", "Rating": 4.33, "ISBN": "9780374528379", "Description": "A philosophical novel about faith, doubt, and morality centered on a murder within a dysfunctional family."},
    {"Title": "Great Expectations", "Author": "Charles Dickens", "Genre": "Classics", "Rating": 3.77, "ISBN": "9780141439563", "Description": "An orphan nicknamed Pip rises from humble beginnings through a mysterious benefactor in Victorian England."},
    {"Title": "Moby-Dick", "Author": "Herman Melville", "Genre": "Classics", "Rating": 3.50, "ISBN": "9780142437247", "Description": "Captain Ahab obsessively pursues the great white whale across the seas in this epic tale of obsession."},
]


def _extract_first_genre(genre_str: str) -> str:
    """Return the first genre from a list-string or comma/pipe/slash-separated string."""
    if not isinstance(genre_str, str):
        return ""
    # Handle Python list strings like "['Fantasy', 'Young Adult']"
    s = genre_str.strip()
    if s.startswith("["):
        try:
            items = ast.literal_eval(s)
            if isinstance(items, list) and items:
                return str(items[0]).strip()
        except (ValueError, SyntaxError):
            pass
    for sep in [",", "|", "/"]:
        if sep in genre_str:
            return genre_str.split(sep)[0].strip()
    return genre_str.strip()


def load_dataset(csv_path: str = "Book_Details.csv", max_rows: int = 20000) -> pd.DataFrame:
    """
    Load and preprocess a book dataset.

    Priority:
      1. Book_Details.csv (default)
      2. Any other CSV at csv_path
      3. Built-in sample dataset

    Returns a cleaned DataFrame with columns:
      Title, Author, Genre, Rating, ISBN, Description, CoverURL
    """

    # ---- Try loading the CSV ----
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, on_bad_lines="skip", low_memory=False)

            # Possible column name variants in the wild for this dataset
            col_map = {}
            lower_cols = {c.lower(): c for c in df.columns}

            for target, candidates in {
                "Title":       ["book_title", "title", "name"],
                "Author":      ["author", "authors", "book_author"],
                "Genre":       ["genres", "genre", "categories", "shelves"],
                "Rating":      ["average_rating", "rating", "avg_rating", "book_average_rating"],
                "ISBN":        ["isbn", "isbn13", "isbn_13"],
                "Description": ["book_details", "desc", "description", "synopsis", "summary", "book_desc"],
                "CoverURL":    ["cover_image_uri", "cover_url", "image_url", "thumbnail"],
            }.items():
                for cand in candidates:
                    if cand in lower_cols:
                        col_map[lower_cols[cand]] = target
                        break

            df = df.rename(columns=col_map)

            # Keep only the columns that we managed to map
            keep_cols = ["Title", "Author", "Genre", "Rating", "ISBN", "Description", "CoverURL"]
            available = [c for c in keep_cols if c in df.columns]
            required = [c for c in available if c not in ("ISBN", "CoverURL")]
            df = df[available].dropna(subset=required)

            # Ensure Rating is numeric
            if "Rating" in df.columns:
                df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
                df = df.dropna(subset=["Rating"])
                df = df[df["Rating"] >= 3.0]

            # First genre only
            if "Genre" in df.columns:
                df["Genre"] = df["Genre"].apply(_extract_first_genre)
                df = df[df["Genre"].str.strip() != ""]

            # Ensure optional columns exist
            if "ISBN" not in df.columns:
                df["ISBN"] = ""
            if "CoverURL" not in df.columns:
                df["CoverURL"] = ""

            # Drop duplicate titles (keep first / highest rated)
            df = df.drop_duplicates(subset=["Title"], keep="first")

            # Limit rows for performance
            if len(df) > max_rows:
                df = df.sample(n=max_rows, random_state=42)

            df = df.reset_index(drop=True)

            if len(df) > 0:
                print(f"[data_loader] Loaded {len(df)} books from {csv_path}.")
                return df

        except Exception as exc:
            print(f"[data_loader] Could not read CSV ({exc}). Falling back to sample data.")

    # ---- Fallback: built-in sample ----
    print(f"[data_loader] Using built-in sample dataset ({len(SAMPLE_BOOKS)} books).")
    df = pd.DataFrame(SAMPLE_BOOKS)
    df["Genre"] = df["Genre"].apply(_extract_first_genre)
    if "CoverURL" not in df.columns:
        df["CoverURL"] = ""
    df = df.reset_index(drop=True)
    return df
