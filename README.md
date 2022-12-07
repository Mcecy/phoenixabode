# Phoenix' Abode
## **Video Demo**:  https://youtu.be/BD4s-WpRK-g
## **Description**
Phoenix' Abode is a novel reading website. You can register as an user and be later flagged as staff if needed.
### **Homepage**
On the homepage, you'll see the options for logging in or register, as well as a list of the novels available for reading (which you won't have access to unless you're logged in).
### **Navigation Bar for Reader**
If you're logged in as a regular user, a reader, you'll see only the options for the homepage, novels' list, profile and logout.
### **Novels**
Here you can see all the novels available for reading, their id, title, chapter count, author and status. You can click on a title to be directed to its page.
### **Novel Page**
On this page you'll have all the information you need on the chosen novel: title, author, sinopsis and chapters. You can also choose to save the novel on your library.
### **Chapter Page**
when choosing a chapter on the novel page, you'll be directed to its content where you'll see the title for the novel, chapter title and the chapter content itself.
### **Profile**
On the profile page, you'll have your profile picture and your information, as well as access to your library and for editing your profile information.
### **Library**
On your library you'll have the content presented the same as in the Novels Page, but only the titles you saved to your library will be shown.
### **Search**
You can search any novel based on part of the title. The search page will show all and any that fit the search term.

### **Navigation Bar for Staff**
When logged in as staff, you'll see all the options for the reader on the navigation bar, plus the post chapter and add novel options.

### **Add novel**
You choose this option when you want to add a new novel to the system. You put its title, author and sinopsis for starters. When done, you'll be redirected to the new novel's page.
### **Post Chapter**
This option is for when you, as staff, want to add a new chapter to an existing novel. You put the novel's title, chapter's number, chapter's title and its content. When done, you'll be redirected to the new chapter's page.
## **Files**
### **app.py**
Where most of the backend code is. Configurations for each of the templates and routes, as well as redirections and transactions with the database.
### **helpers.py**
Code for helper functions like login required and admin required wraps, as well as the error page helper.
### **phoenixabode.db**
Sqlite3 database for the website. Schemas for users, novels, authors, staff roles (yet to be implemented), chapters, triggers for computed columns, and unique indexes.
### **requirements.txt**
Libraries used on the flask app.
