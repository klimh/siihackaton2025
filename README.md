------------------ENGLISH BELOW------------------------------

# 🩺 Mordzia Health Support – Hackathon 2025

**Projekt przygotowany przez zespół _papa roach_ w składzie:**

- Klim Hudzenko _(lider)_
- Maciej Miazek
- Kacper Błaszczyk
- Konrad Kuberski


# Opis Projektu: Aplikacja Wspierająca Zdrowie Psychiczne

## Przegląd projektu

Aplikacja webowa stworzona w celu wspierania zdrowia psychicznego użytkowników poprzez kompleksowe narzędzia do monitorowania, analizy i poprawy dobrostanu psychicznego. Projekt wykorzystuje nowoczesne technologie webowe i sztuczną inteligencję do zapewnienia spersonalizowanego wsparcia.

### Grupa docelowa
- Osoby dbające o swoje zdrowie psychiczne i dobrostan
- Użytkownicy poszukujący narzędzi do samokontroli i rozwoju
- Administratorzy monitorujący postępy i wspierający użytkowników
- Osoby potrzebujące regularnego wsparcia i monitoringu nastroju

## Obecne funkcjonalności

### 1. System autentykacji i zarządzania użytkownikami
- Rejestracja z wyborem spersonalizowanego awatara
- Logowanie z zabezpieczeniami (Flask-Login, Flask-Bcrypt)
- Role użytkowników (user/admin) z różnymi poziomami dostępu
- Personalizacja profilu z wyborem motywu (jasny/ciemny)
- System awatarów (predefiniowane oraz możliwość dodania własnego)

### 2. Monitorowanie nastroju i samopoczucia
- Dzienny dziennik nastroju (skala 1-10)
- Możliwość dodawania notatek do wpisów
- Automatyczna analiza trendów nastroju
- Wizualizacja danych w formie wykresów
- Statystyki i odchylenia nastroju

### 3. Inteligentny czat wsparcia
- Konwersacje z AI analizujące kontekst
- Analiza sentymentu wypowiedzi
- Zapisywanie historii rozmów
- Personalizowane odpowiedzi bazujące na historii użytkownika
- Automatyczne sugestie wsparcia

### 4. System ankiet i aktywności
- Codzienne ankiety dotyczące aktywności
- Monitorowanie czasu spędzonego w mediach społecznościowych
- Możliwość dodawania własnych aktywności
- Śledzenie różnych typów aktywności (medytacja, kroki, oddychanie)
- Statystyki i trendy aktywności

### 5. Zarządzanie zadaniami i kalendarz
- Lista zadań z możliwością oznaczania jako wykonane
- Kalendarz aktywności z kolorowym oznaczeniem typów
- Planowanie działań wspierających dobrostan
- Przypomnienia o zaplanowanych aktywnościach
- Wizualizacja postępów

### 6. System raportowania
- Generowanie szczegółowych raportów PDF
- Wykresy i statystyki w raportach
- Analiza długoterminowych trendów
- Eksport danych do różnych formatów
- Automatyczne podsumowania okresowe

### 7. Panel administracyjny
- Monitoring aktywności użytkowników
- Przegląd raportów i statystyk
- Zarządzanie kontami użytkowników
- Analiza wykorzystania systemu pomocy
- Statystyki zaangażowania

### 8. System pomocy i wsparcia
- Lista kontaktów pomocowych
- Telefony zaufania i kontakty do specjalistów
- Automatyczne powiadomienia o potrzebie wsparcia
- Śledzenie dostępu do systemu pomocy
- Dynamiczna zmiana interfejsu based na stanie użytkownika

## Stos technologiczny

### Backend
- Python 3.8+
- Flask (framework webowy)
- Flask-SQLAlchemy (ORM)
- Flask-Login (autentykacja)
- Flask-Bcrypt (haszowanie haseł)
- SQLite (baza danych)

### Frontend
- Tailwind CSS (via CDN)
- JavaScript (vanilla)
- HTML5
- Font Awesome (ikony)

### Narzędzia analityczne i raportowanie
- Matplotlib (generowanie wykresów)
- NumPy (analiza danych)
- ReportLab (generowanie PDF)
- TextBlob (analiza sentymentu)

## Przepływ danych

### 1. Zbieranie danych
- Wpisy dziennika nastroju
- Odpowiedzi w ankietach
- Logi aktywności
- Historia konwersacji z AI
- Odpowiedzi na pytania

### 2. Przetwarzanie
- Analiza sentymentu wiadomości
- Obliczanie statystyk nastroju
- Agregacja danych aktywności
- Generowanie wskaźników dobrostanu

### 3. Prezentacja
- Wykresy w interfejsie użytkownika
- Raporty PDF
- Powiadomienia i alerty
- Statystyki w panelu admina

## Bezpieczeństwo

### Autentykacja i autoryzacja
- Haszowanie haseł (Flask-Bcrypt)
- Sesje użytkowników (Flask-Login)
- System ról (user/admin)
- Zabezpieczenia CSRF

### Ochrona danych
- Walidacja danych wejściowych
- Sanityzacja danych
- Bezpieczne przechowywanie w SQLite
- Szyfrowanie wrażliwych informacji

## Propozycje rozszerzeń

### A. Zaangażowanie użytkowników

1. System osiągnięć i odznak
   - Opis: Gamifikacja aktywności użytkowników
   - Korzyści: Zwiększenie motywacji i regularności korzystania
   - Implementacja: Nowy model Achievement, system przyznawania punktów

2. Społeczność i grupy wsparcia
   - Opis: Możliwość tworzenia i dołączania do grup wsparcia
   - Korzyści: Wzajemne wsparcie użytkowników
   - Implementacja: Nowe modele Group i Membership, system moderacji

3. Personalizowane wyzwania
   - Opis: System tworzenia i realizacji wyzwań dobrostanu
   - Korzyści: Motywacja do regularnych działań
   - Implementacja: Model Challenge, system śledzenia postępów

4. Integracja z urządzeniami fitness
   - Opis: Synchronizacja z trackerami aktywności
   - Korzyści: Automatyczne śledzenie aktywności fizycznej
   - Implementacja: API dla popularnych urządzeń (Fitbit, Garmin)

5. System medytacji guidowanych
   - Opis: Biblioteka medytacji z prowadzeniem
   - Korzyści: Wsparcie praktyki mindfulness
   - Implementacja: System audio, timer medytacji

### B. Analityka i raporty

6. Zaawansowana analiza predykcyjna
   - Opis: Przewidywanie trendów nastroju
   - Korzyści: Wczesne wykrywanie problemów
   - Implementacja: Machine Learning (scikit-learn)

7. Eksport danych w różnych formatach
   - Opis: Możliwość eksportu do CSV, JSON, Excel
   - Korzyści: Łatwiejsza integracja z innymi narzędziami
   - Implementacja: Biblioteki pandas, openpyxl

8. Interaktywne dashboardy
   - Opis: Rozbudowane wizualizacje danych
   - Korzyści: Lepsze zrozumienie trendów
   - Implementacja: Plotly lub D3.js

### C. Komunikacja i powiadomienia

9. System powiadomień email
   - Opis: Przypomnienia i raporty via email
   - Korzyści: Zwiększenie zaangażowania
   - Implementacja: Flask-Mail, szablony email

10. Powiadomienia push
    - Opis: Natychmiastowe powiadomienia w przeglądarce
    - Korzyści: Szybka reakcja na ważne wydarzenia
    - Implementacja: Service Workers, WebPush

11. Integracja z komunikatorami
    - Opis: Wysyłanie przypomnień przez Telegram/WhatsApp
    - Korzyści: Większa dostępność
    - Implementacja: API komunikatorów

### D. Narzędzia administracyjne

12. Zaawansowany system raportowania
    - Opis: Więcej opcji analizy dla adminów
    - Korzyści: Lepsze zarządzanie systemem
    - Implementacja: Nowe widoki i filtry

13. System moderacji treści
    - Opis: Narzędzia do moderacji wpisów i komentarzy
    - Korzyści: Bezpieczniejsze środowisko
    - Implementacja: System flagowania, kolejka moderacji

14. Panel zarządzania treścią
    - Opis: CMS dla artykułów i porad
    - Korzyści: Łatwiejsze zarządzanie treścią
    - Implementacja: Flask-Admin, edytor WYSIWYG

### E. Integracje zewnętrzne

15. Integracja z kalendarzem
    - Opis: Synchronizacja z Google Calendar
    - Korzyści: Lepsze planowanie aktywności
    - Implementacja: Google Calendar API

16. API dla zewnętrznych aplikacji
    - Opis: REST API dla integracji
    - Korzyści: Możliwość tworzenia aplikacji mobilnych
    - Implementacja: Flask-RESTful

17. Integracja z asystentami głosowymi
    - Opis: Wsparcie dla Alexa/Google Assistant
    - Korzyści: Łatwiejszy dostęp do funkcji
    - Implementacja: API asystentów głosowych

## Podsumowanie

Projekt oferuje kompleksowe narzędzie do wspierania zdrowia psychicznego, łącząc nowoczesne technologie z praktycznymi funkcjami. Proponowane rozszerzenia pozwolą na dalszy rozwój i lepsze dostosowanie do potrzeb użytkowników.


----------ENGLISH--------------

# 🩺 Mordzia Health Support – Hackathon 2025

**Project has been created by team _papa roach_ including:**

- Klim Hudzenko _(lider)_
- Maciej Miazek
- Kacper Błaszczyk
- Konrad Kuberski

# Project Description: Mental Health Support Application

## Project Overview

A web application designed to support users' mental health through comprehensive tools for monitoring, analyzing, and improving psychological well-being. The project utilizes modern web technologies and artificial intelligence to provide personalized support.

### Target Audience:
- Individuals caring about mental health and well-being
- Users seeking self-monitoring and development tools
- Administrators monitoring progress and supporting users

## Current Features

### 1. Authentication and User Management System
- Registration with personalized avatar selection
- Secure login (Flask-Login, Flask-Bcrypt)
- User roles (user/admin) with different access levels
- Profile personalization with theme choice (light/dark)

### 2. Mood Monitoring
- Daily mood journal (1-10 scale)
- Option to add notes to entries
- Mood trend visualization
- Automatic statistical analysis (averages, deviations)

### 3. Intelligent Support Chat
- Context-aware AI conversations
- Sentiment analysis of messages
- Conversation history with review capability
- Personalized responses based on user history

### 4. Survey and Activity System
- Daily activity surveys
- Social media time monitoring
- Custom activity addition capability
- Tracking various activity types (meditation, steps, breathing exercises)

### 5. Task Management and Calendar
- Task list with completion marking
- Activity calendar with color-coded types
- Scheduled task reminders
- Progress visualization

### 6. Reporting System
- Detailed PDF report generation
- Charts and statistics using matplotlib
- Long-term trend analysis
- Data export in various formats

### 7. Admin Panel
- Overview of all user statistics
- Activity and progress monitoring
- User account management
- Aggregate report generation

### 8. Help and Support System
- Helpful contact list
- Automatic low mood notifications
- Help resource access tracking
- Dynamic interface changes based on user state

## Technology Stack

### Backend:
- Python 3.8+
- Flask (web framework)
- Flask-SQLAlchemy (ORM)
- Flask-Login (authentication)
- Flask-Bcrypt (password hashing)
- SQLite (database)

### Frontend:
- Tailwind CSS (via CDN)
- JavaScript (vanilla)
- HTML5
- Responsive Design

### Tools and Libraries:
- Matplotlib (chart generation)
- ReportLab (PDF generation)
- NumPy (data analysis)
- TextBlob (sentiment analysis)

## Data Flow

1. Data Collection:
   - User mood entries
   - Survey responses
   - Activity and task logs
   - AI conversation history

2. Processing:
   - Message sentiment analysis
   - Mood statistics calculation
   - Visualization generation
   - Report creation

3. Storage:
   - SQLite for all user data
   - File system for avatars and reports
   - Secure password storage (bcrypt)

## Security

1. Authentication:
   - Password hashing (Flask-Bcrypt)
   - User sessions (Flask-Login)
   - Brute-force attack protection

2. Authorization:
   - Role system (user/admin)
   - Resource access control
   - Permission validation

3. Data Protection:
   - CSRF protection
   - Input data sanitization
   - Secure file storage

## Proposed Extensions

### A. User Engagement

1. Achievement and Badge System
   - Description: Gamification of user activities
   - Benefits: Increased motivation and engagement
   - Implementation: New Achievement model, integration with existing activities

2. Community and Support Groups
   - Description: Ability to create and join support groups
   - Benefits: Peer support among users
   - Implementation: New Group and Membership models

3. Goals and Challenges System
   - Description: Define personal health goals
   - Benefits: Personal development structuring
   - Implementation: Goal model with progress tracking

4. Personalized Development Paths
   - Description: AI-driven activity recommendations
   - Benefits: Better user needs matching
   - Implementation: ML algorithms for pattern analysis

5. Interactive Mindfulness Exercises
   - Description: Guided meditations and exercises
   - Benefits: Practical development tools
   - Implementation: Audio/video library integration

### B. Analytics and Reports

6. Advanced Predictive Analysis
   - Description: Mood trend prediction
   - Benefits: Proactive support
   - Implementation: ML models (scikit-learn)

7. Multi-Format Data Export
   - Description: Export to CSV, JSON, PDF
   - Benefits: Better data portability
   - Implementation: New API endpoints

8. Interactive Dashboards
   - Description: Advanced D3.js visualizations
   - Benefits: Better data understanding
   - Implementation: D3.js integration

### C. Integrations

9. Fitness Device Integration
   - Description: Activity tracker synchronization
   - Benefits: Automatic tracking
   - Implementation: Fitness tracker APIs

10. Push Notifications
    - Description: Web and mobile notifications
    - Benefits: Better engagement
    - Implementation: Service Workers, Firebase

11. Google/Outlook Calendar
    - Description: Task and reminder synchronization
    - Benefits: Better organization
    - Implementation: OAuth2, Calendar APIs

### D. Administrative Tools

12. Content Moderation System
    - Description: Group and comment moderation tools
    - Benefits: Safer community
    - Implementation: Moderator panel

13. Advanced Statistics
    - Description: Detailed admin analytics
    - Benefits: Better user understanding
    - Implementation: New analytical views

14. Automated Reporting
    - Description: Periodic admin reports
    - Benefits: Proactive monitoring
    - Implementation: Cron tasks

### E. Security and Privacy

15. Two-Factor Authentication
    - Description: Additional security layer
    - Benefits: Enhanced security
    - Implementation: Flask-Security

16. End-to-End Encryption
    - Description: Sensitive data encryption
    - Benefits: Better privacy protection
    - Implementation: Cryptographic libraries

## Summary

The application serves as a comprehensive tool for supporting mental health, combining modern technologies with practical personal development tools. The proposed extensions would significantly enhance the system's functionality and usability while maintaining its modular structure and leveraging the existing technology stack. 

 
