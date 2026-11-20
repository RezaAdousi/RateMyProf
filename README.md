# RateMyProf
#### Video Demo: https://youtu.be/S8dOWWSjhfU  
#### Description:

RateMyProf is a web-based application designed to help university students make more informed decisions when choosing professors for their courses. The platform allows students to rate professors, leave textual reviews, and view aggregated feedback from other students. In addition to traditional user-generated reviews, the application integrates artificial intelligence to generate concise and structured summaries of student feedback once a sufficient number of reviews are available.

At my university, choosing professors is often a challenging and stressful process. Students usually rely on informal advice from upperclassmen, private messaging groups, or word-of-mouth recommendations, which are often incomplete, biased, or inconsistent. RateMyProf aims to centralize this information in a structured, transparent, and accessible way, allowing students to easily compare professors based on real experiences shared by their peers.

---

## Core Features

The application includes several core features that together create a complete and user-friendly experience:

- **User Authentication**: Users can register, log in, and log out securely. Authentication is required to submit reviews, ensuring accountability and reducing spam.
- **Professor Profiles**: Each professor has a dedicated profile page displaying their name, department, photo, average rating, individual reviews, and an AI-generated summary.
- **Review System**: Students can submit a numerical rating (from 1 to 5) along with a written comment describing their experience with a professor.
- **Review Restrictions**: Each user is limited to one review per professor. This design choice prevents users from manipulating ratings by submitting multiple reviews.
- **Review Management**: Users can delete their own reviews at any time. When a review is removed, the professor’s average rating and AI summary are updated automatically.
- **AI-Powered Summaries**: After a professor receives at least three reviews, the system generates an AI-based summary that highlights commonly mentioned strengths and weaknesses.
- **User Profiles**: Users can view their own profile as well as the profiles of other users, including basic information and review history.
- **Search Functionality**: Professors can be searched by name or department directly from the homepage.

---

## AI Summary System

One of the most important and distinguishing aspects of this project is the AI-generated summary feature. Once a professor has at least three reviews, all associated comments are sent to an AI model for analysis and summarization.

The AI model is strictly instructed to:
- Use only information explicitly stated in student reviews
- Avoid assumptions, exaggerations, or fabricated details
- Separate positive points, negative points, and an overall conclusion
- Output the summary in clean and safe HTML format
- Clearly label the rating as AI-estimated, distinct from user ratings

Whenever a review is added or deleted, the summary is automatically regenerated to reflect the most current feedback. This ensures that the AI output always remains consistent with the available data.

---

## Technical Overview

RateMyProf is implemented using a combination of modern web technologies:

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, and Jinja2 templates
- **AI & NLP**:
  - Hugging Face sentiment analysis pipeline for detecting sentiment polarity
  - Hugging Face Inference API (via an OpenAI-compatible client) for text summarization

The project follows a simple MVC-style architecture, separating routing logic, database models, and templates. This structure improves readability, maintainability, and future extensibility.

---

## Database Design

The database consists of three main models:

- **User**: Stores user credentials and profile-related information
- **Professor**: Stores professor metadata, department, and aggregated ratings
- **Review**: Stores review text, numerical rating, sentiment label, timestamps, and foreign keys

Each review creates a relationship between a user and a professor, ensuring relational consistency and enabling constraints such as one-review-per-user-per-professor.

---

### Environment Variables

This project uses environment variables to store sensitive information such as secret keys and API tokens. These values are loaded from a `.env` file during development but are not included in the submission for security reasons.

---

## Design Decisions

Several important design decisions were made during development:

- **Single Review Constraint**: Limiting users to one review per professor improves fairness and data quality.
- **Minimum Review Threshold for AI**: Requiring at least three reviews before generating summaries increases reliability.
- **Server-Side Validation**: All critical rules are enforced on the backend to prevent manipulation through client-side requests.
- **HTML-Based AI Output**: Generating HTML allows structured rendering while maintaining control over formatting.

---

## Future Improvements

Potential future enhancements include:
- Email verification during registration
- Editing existing reviews instead of only deleting them
- Sorting and filtering reviews by rating or date
- Pagination for large numbers of reviews
- Deployment using a production-grade database
- A localized version customized specifically for my university

---

## Conclusion

RateMyProf is a practical and scalable web application that combines traditional web development concepts with modern AI capabilities. It addresses a real-world problem faced by students and demonstrates skills in backend development, database design, authentication, and AI integration. This project reflects the core principles taught in CS50 while extending them into a meaningful and realistic application.
