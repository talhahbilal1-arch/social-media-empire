#!/usr/bin/env python3
"""
Generate a high-quality Menopause Symptom Tracker PDF (free lead magnet).
Sage green + dusty rose branding. 14 pages of real, usable content.
"""
import os
from fpdf import FPDF


def sanitize(text):
    """Replace Unicode chars with latin-1 safe equivalents for Helvetica."""
    return (text
        .replace('\u2014', '--')   # em dash
        .replace('\u2013', '-')    # en dash
        .replace('\u2018', "'")    # left single quote
        .replace('\u2019', "'")    # right single quote
        .replace('\u201c', '"')    # left double quote
        .replace('\u201d', '"')    # right double quote
        .replace('\u2026', '...')  # ellipsis
        .replace('\u00d7', 'x')   # multiplication sign
        .replace('\u2022', '-')   # bullet
    )

# ── Brand Colors ──────────────────────────────────
SAGE = (124, 154, 130)
SAGE_LIGHT = (168, 197, 174)
SAGE_DARK = (90, 122, 96)
ROSE = (201, 145, 143)
ROSE_LIGHT = (232, 196, 194)
CHARCOAL = (45, 52, 54)
TEXT = (61, 61, 61)
TEXT_MUTED = (107, 114, 128)
CREAM = (250, 248, 245)
WHITE = (255, 255, 255)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "outputs", "menopause-planner-website")


class TrackerPDF(FPDF):
    """Custom PDF with menopause tracker branding."""

    def __init__(self):
        super().__init__('P', 'mm', 'Letter')
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(18, 18, 18)

    def cell(self, w=0, h=0, text='', *args, **kwargs):
        return super().cell(w, h, sanitize(str(text)), *args, **kwargs)

    def multi_cell(self, w, h=0, text='', *args, **kwargs):
        return super().multi_cell(w, h, sanitize(str(text)), *args, **kwargs)

    def _brand_header_bar(self, color=SAGE):
        """Draw a colored bar across the top of the page."""
        self.set_fill_color(*color)
        self.rect(0, 0, 215.9, 12, 'F')

    def _page_footer_text(self, text="The Menopause Planner — Free Symptom Tracker"):
        """Subtle footer on content pages."""
        self.set_y(-15)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 5, text, align='C')
        self.cell(0, 5, f'Page {self.page_no() - 1}', align='R')

    def _section_title(self, title, color=SAGE_DARK):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(*color)
        self.cell(0, 12, title, ln=True)
        # Underline
        self.set_draw_color(*color)
        self.set_line_width(0.8)
        self.line(18, self.get_y() + 1, 100, self.get_y() + 1)
        self.ln(6)

    def _body_text(self, text, size=10):
        self.set_font('Helvetica', '', size)
        self.set_text_color(*TEXT)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def _bold_text(self, text, size=10):
        self.set_font('Helvetica', 'B', size)
        self.set_text_color(*CHARCOAL)
        self.multi_cell(0, 5.5, text)

    def _bullet_point(self, text, bullet_color=SAGE):
        x = self.get_x()
        y = self.get_y()
        self.set_fill_color(*bullet_color)
        self.ellipse(x, y + 1.5, 3, 3, 'F')
        self.set_x(x + 6)
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(*TEXT)
        self.multi_cell(160, 5, text)
        self.ln(1.5)

    def _checkbox_line(self, text, indent=0):
        x = 18 + indent
        y = self.get_y()
        self.set_draw_color(*SAGE)
        self.set_line_width(0.4)
        self.rect(x, y, 4, 4)
        self.set_x(x + 7)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*TEXT)
        self.cell(0, 5, text, ln=True)
        self.ln(1)

    def _tracking_row(self, label, cols=7, row_height=8):
        """Draw a labeled tracking row with empty cells."""
        x_start = 18
        label_w = 42
        cell_w = (179.9 - label_w) / cols

        y = self.get_y()
        # Label cell
        self.set_fill_color(*CREAM)
        self.set_draw_color(*SAGE_LIGHT)
        self.set_line_width(0.3)
        self.rect(x_start, y, label_w, row_height, 'FD')
        self.set_xy(x_start + 2, y)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*CHARCOAL)
        self.cell(label_w - 4, row_height, label, align='L')

        # Data cells
        for i in range(cols):
            cx = x_start + label_w + (i * cell_w)
            self.set_fill_color(*WHITE)
            self.rect(cx, y, cell_w, row_height, 'FD')

        self.set_y(y + row_height)

    def _day_header_row(self, cols=7, row_height=7):
        """Draw day-of-week header row."""
        x_start = 18
        label_w = 42
        cell_w = (179.9 - label_w) / cols
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        y = self.get_y()
        # Empty label cell
        self.set_fill_color(*SAGE)
        self.rect(x_start, y, label_w, row_height, 'F')
        self.set_xy(x_start + 2, y)
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(*WHITE)
        self.cell(label_w - 4, row_height, 'SYMPTOM', align='L')

        for i, day in enumerate(days):
            cx = x_start + label_w + (i * cell_w)
            self.set_fill_color(*SAGE)
            self.rect(cx, y, cell_w, row_height, 'F')
            self.set_xy(cx, y)
            self.set_font('Helvetica', 'B', 7)
            self.set_text_color(*WHITE)
            self.cell(cell_w, row_height, day, align='C')

        self.set_y(y + row_height)


def build_cover(pdf):
    """Page 1: Cover page."""
    pdf.add_page()
    # Full sage background
    pdf.set_fill_color(*SAGE)
    pdf.rect(0, 0, 215.9, 279.4, 'F')

    # Decorative circles
    pdf.set_fill_color(*SAGE_LIGHT)
    pdf.set_draw_color(*SAGE_LIGHT)
    pdf.ellipse(150, -30, 120, 120, 'F')
    pdf.set_fill_color(*SAGE_DARK)
    pdf.ellipse(-40, 200, 100, 100, 'F')

    # White content card
    pdf.set_fill_color(*WHITE)
    pdf.rect(30, 55, 155.9, 160, 'F')

    # Title
    pdf.set_xy(35, 68)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(*CHARCOAL)
    pdf.multi_cell(145, 12, 'Menopause\nSymptom Tracker')

    # Divider
    pdf.set_draw_color(*ROSE)
    pdf.set_line_width(1.5)
    pdf.line(35, 108, 85, 108)

    # Subtitle
    pdf.set_xy(35, 115)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(*TEXT)
    pdf.multi_cell(140, 6.5,
        'Track your symptoms, identify triggers,\n'
        'and take control of your menopause journey.\n\n'
        'A daily tracking system to help you\n'
        'and your doctor find what works for YOU.')

    # Rose accent box
    pdf.set_fill_color(*ROSE_LIGHT)
    pdf.rect(35, 160, 140, 22, 'F')
    pdf.set_xy(40, 163)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*ROSE)
    pdf.cell(0, 6, 'FREE RESOURCE')
    pdf.set_xy(40, 170)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*TEXT)
    pdf.cell(0, 6, 'from The Menopause Planner  |  menopauseplanner.com')

    # Bottom branding
    pdf.set_xy(30, 230)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*WHITE)
    pdf.cell(155.9, 5, 'menopause-planner-website.vercel.app', align='C')


def build_welcome(pdf):
    """Page 2: Welcome + How to Use."""
    pdf.add_page()
    pdf._brand_header_bar(SAGE)
    pdf.set_y(22)

    pdf._section_title('Welcome to Your Tracker')

    pdf._body_text(
        "You're not imagining it. The hot flashes at 3pm, the insomnia at 2am, "
        "the brain fog that makes you forget why you walked into a room — these are "
        "real symptoms with real triggers. And the first step to managing them is "
        "understanding YOUR unique patterns."
    )
    pdf.ln(2)
    pdf._body_text(
        "This tracker is designed to help you connect the dots between what you eat, "
        "how you sleep, your stress levels, and the intensity of your symptoms. After "
        "just 2-4 weeks of consistent tracking, most women discover surprising patterns "
        "they never noticed before."
    )
    pdf.ln(4)

    pdf._bold_text('How to Use This Tracker:', 12)
    pdf.ln(3)

    steps = [
        ("Track daily (it takes 2 minutes)", "Fill in your symptom tracker each evening before bed. Rate each symptom 0-5 where 0 = none and 5 = severe."),
        ("Log your food triggers", "Use the Food & Sugar Trigger Log to note what you ate, especially sugar, caffeine, and alcohol. Look for patterns 4-8 hours after consumption."),
        ("Note your sleep quality", "Poor sleep amplifies every other symptom. The sleep tracker helps you identify what's disrupting your rest."),
        ("Review weekly", "At the end of each week, look at your patterns. Do hot flashes spike on high-sugar days? Does exercise improve your mood scores?"),
        ("Bring it to your doctor", "Your completed tracker gives your healthcare provider actual data instead of vague descriptions. This leads to better, personalized treatment."),
    ]

    for i, (title, desc) in enumerate(steps, 1):
        y = pdf.get_y()
        # Number circle
        pdf.set_fill_color(*SAGE)
        pdf.ellipse(18, y, 8, 8, 'F')
        pdf.set_xy(18, y + 0.5)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*WHITE)
        pdf.cell(8, 7, str(i), align='C')
        # Text
        pdf.set_xy(30, y)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*CHARCOAL)
        pdf.cell(0, 6, title, ln=True)
        pdf.set_x(30)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*TEXT)
        pdf.multi_cell(148, 4.8, desc)
        pdf.ln(4)

    pdf.ln(4)
    # Tip box
    pdf.set_fill_color(*ROSE_LIGHT)
    pdf.rect(18, pdf.get_y(), 179.9, 24, 'F')
    pdf.set_xy(23, pdf.get_y() + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*ROSE)
    pdf.cell(0, 5, 'PRO TIP')
    pdf.set_xy(23, pdf.get_y() + 7)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*TEXT)
    pdf.multi_cell(168, 4.5,
        "Research shows that sugar spikes can trigger hot flashes within 2-4 hours. "
        "Pay special attention to the food log — it's often the most revealing section.")

    pdf._page_footer_text()


def build_baseline_assessment(pdf):
    """Page 3: My Baseline Assessment checklist."""
    pdf.add_page()
    pdf._brand_header_bar(ROSE)
    pdf.set_y(22)

    pdf._section_title('My Baseline Assessment', ROSE)

    pdf._body_text(
        "Before you start tracking, take a snapshot of where you are right now. "
        "Check all symptoms you currently experience and rate their severity (1=mild, 5=severe). "
        "Revisit this page in 30 days to see how things have changed."
    )
    pdf.ln(2)

    pdf._bold_text('Date: ___ / ___ / ______          Age: _______', 10)
    pdf.ln(4)

    categories = {
        'Vasomotor Symptoms': [
            'Hot flashes (daytime)',
            'Night sweats',
            'Heart palpitations',
            'Flushing / facial redness',
        ],
        'Mood & Cognitive': [
            'Anxiety or panic attacks',
            'Irritability / mood swings',
            'Brain fog / poor concentration',
            'Memory lapses',
            'Feeling overwhelmed',
            'Low mood / sadness',
        ],
        'Sleep': [
            'Difficulty falling asleep',
            'Waking at 2-4 AM',
            'Restless / light sleep',
            'Daytime fatigue',
        ],
        'Physical': [
            'Joint or muscle pain',
            'Weight gain (especially midsection)',
            'Headaches / migraines',
            'Bloating / digestive changes',
            'Hair thinning',
            'Dry skin / itching',
        ],
        'Other': [
            'Vaginal dryness',
            'Low libido',
            'Urinary urgency',
            'Tingling extremities',
        ],
    }

    for cat_name, items in categories.items():
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*SAGE_DARK)
        pdf.cell(0, 6, cat_name.upper(), ln=True)
        pdf.ln(1)
        for item in items:
            pdf._checkbox_line(f'{item}                                         Severity:  1   2   3   4   5')
        pdf.ln(2)

    pdf._page_footer_text()


def build_weekly_tracker(pdf, week_num):
    """One weekly symptom tracking page."""
    pdf.add_page()
    pdf._brand_header_bar(SAGE)
    pdf.set_y(22)

    pdf._section_title(f'Week {week_num} — Daily Symptom Tracker')

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(0, 5, 'Rate each symptom 0-5 (0 = none, 5 = severe). Track at the same time each day for consistency.', ln=True)
    pdf.ln(1)

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*TEXT)
    pdf.cell(0, 5, f'Week starting:  ___ / ___ / ______', ln=True)
    pdf.ln(4)

    # Header row
    pdf._day_header_row()

    symptoms = [
        'Hot flashes',
        'Night sweats',
        'Mood (low=bad)',
        'Anxiety level',
        'Brain fog',
        'Energy level',
        'Sleep quality',
        'Joint pain',
        'Headache',
        'Bloating',
        'Irritability',
        'Weight (lbs)',
    ]

    for s in symptoms:
        pdf._tracking_row(s)

    pdf.ln(5)

    # Notes section
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*SAGE_DARK)
    pdf.cell(0, 5, 'WEEKLY NOTES & OBSERVATIONS', ln=True)
    pdf.ln(2)
    pdf.set_draw_color(*SAGE_LIGHT)
    pdf.set_line_width(0.3)
    for _ in range(5):
        y = pdf.get_y()
        pdf.line(18, y, 197.9, y)
        pdf.ln(7)

    # Pattern check
    y = pdf.get_y()
    if y < 230:
        pdf.ln(2)
        pdf.set_fill_color(*CREAM)
        pdf.rect(18, pdf.get_y(), 179.9, 18, 'F')
        pdf.set_xy(23, pdf.get_y() + 2)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(*SAGE_DARK)
        pdf.cell(0, 5, 'PATTERN CHECK:')
        pdf.set_xy(23, pdf.get_y() + 6)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*TEXT)
        pdf.cell(0, 5, 'Worst symptom day: _________    Best day: _________    Possible trigger: _________________________')

    pdf._page_footer_text()


def build_food_trigger_log(pdf, page_num):
    """Food & Sugar Trigger Log page."""
    pdf.add_page()
    pdf._brand_header_bar(ROSE)
    pdf.set_y(22)

    title = 'Food & Sugar Trigger Log'
    if page_num > 1:
        title += f' (continued)'
    pdf._section_title(title, ROSE)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.multi_cell(0, 4.5,
        'Log meals, snacks, and drinks — especially sugar, caffeine, and alcohol. '
        'Note any symptoms within 2-8 hours. This is often the most eye-opening page.')
    pdf.ln(4)

    # Table header
    cols = [('DATE', 20), ('TIME', 15), ('FOOD / DRINK', 60),
            ('SUGAR?', 16), ('CAFFEINE?', 18), ('SYMPTOM AFTER', 50.9)]
    y = pdf.get_y()
    x = 18
    pdf.set_fill_color(*ROSE)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*WHITE)
    for label, w in cols:
        pdf.set_xy(x, y)
        pdf.rect(x, y, w, 7, 'F')
        pdf.cell(w, 7, label, align='C')
        x += w

    pdf.set_y(y + 7)

    # Empty rows
    row_count = 20
    pdf.set_draw_color(*ROSE_LIGHT)
    pdf.set_line_width(0.3)
    for r in range(row_count):
        y = pdf.get_y()
        x = 18
        fill = CREAM if r % 2 == 0 else WHITE
        pdf.set_fill_color(*fill)
        for _, w in cols:
            pdf.rect(x, y, w, 9, 'FD')
            x += w
        pdf.set_y(y + 9)

    pdf.ln(4)
    # Quick reference
    pdf.set_fill_color(*ROSE_LIGHT)
    h = 28
    pdf.rect(18, pdf.get_y(), 179.9, h, 'F')
    pdf.set_xy(23, pdf.get_y() + 2)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*ROSE)
    pdf.cell(0, 5, 'COMMON HIDDEN SUGAR SOURCES TO WATCH FOR:')
    pdf.set_xy(23, pdf.get_y() + 7)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*TEXT)
    pdf.multi_cell(168, 4.2,
        "Yogurt (flavored), granola bars, smoothies, salad dressing, pasta sauce, "
        "bread, dried fruit, 'healthy' cereals, oat milk (sweetened), protein bars, "
        "condiments (ketchup, BBQ sauce), fruit juice, flavored coffee drinks")

    pdf._page_footer_text()


def build_sleep_tracker(pdf):
    """Sleep Quality Tracker page."""
    pdf.add_page()
    pdf._brand_header_bar(SAGE)
    pdf.set_y(22)

    pdf._section_title('Sleep Quality Tracker')

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.multi_cell(0, 4.5,
        'Sleep disruption affects 60% of menopausal women. Tracking your sleep patterns '
        'helps identify whether sugar, caffeine, screen time, or hormonal shifts are the '
        'primary cause of your insomnia.')
    pdf.ln(4)

    # Table header
    cols = [('DATE', 18), ('BEDTIME', 18), ('WAKE TIME', 20), ('HOURS', 14),
            ('QUALITY\n(1-5)', 16), ('NIGHT\nSWEATS', 16), ('WOKE UP\nAT', 18),
            ('NOTES / POSSIBLE CAUSE', 59.9)]
    y = pdf.get_y()
    x = 18
    pdf.set_fill_color(*SAGE)
    pdf.set_font('Helvetica', 'B', 6.5)
    pdf.set_text_color(*WHITE)
    for label, w in cols:
        pdf.set_xy(x, y)
        pdf.rect(x, y, w, 10, 'F')
        pdf.multi_cell(w, 5, label, align='C')
        x += w

    pdf.set_y(y + 10)

    # Rows
    pdf.set_draw_color(*SAGE_LIGHT)
    pdf.set_line_width(0.3)
    for r in range(18):
        y = pdf.get_y()
        x = 18
        fill = CREAM if r % 2 == 0 else WHITE
        pdf.set_fill_color(*fill)
        for _, w in cols:
            pdf.rect(x, y, w, 9.5, 'FD')
            x += w
        pdf.set_y(y + 9.5)

    pdf.ln(3)
    # Tip
    pdf.set_fill_color(*CREAM)
    pdf.rect(18, pdf.get_y(), 179.9, 18, 'F')
    pdf.set_xy(23, pdf.get_y() + 2)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*SAGE_DARK)
    pdf.cell(0, 5, 'SLEEP HYGIENE QUICK WINS:')
    pdf.set_xy(23, pdf.get_y() + 6)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*TEXT)
    pdf.cell(0, 5, 'No caffeine after 12pm  |  No sugar 4hrs before bed  |  Cool room (65-68F)  |  No screens 1hr before  |  Magnesium glycinate at bedtime')

    pdf._page_footer_text()


def build_doctor_prep(pdf):
    """Doctor Visit Prep Worksheet."""
    pdf.add_page()
    pdf._brand_header_bar(ROSE)
    pdf.set_y(22)

    pdf._section_title('Doctor Visit Prep Worksheet', ROSE)

    pdf._body_text(
        "Bring this page to your next appointment. Having organized data helps your "
        "doctor give you better, more personalized advice. Studies show patients who "
        "bring symptom logs get more thorough consultations."
    )
    pdf.ln(2)

    pdf._bold_text('Appointment Date: ___ / ___ / ______     Doctor: ___________________________', 9)
    pdf.ln(6)

    sections = [
        ('MY TOP 3 CONCERNS RIGHT NOW', [
            '1. _____________________________________________________________',
            '2. _____________________________________________________________',
            '3. _____________________________________________________________',
        ]),
        ('CURRENT MEDICATIONS & SUPPLEMENTS', [
            'Medication: ___________________  Dose: _______  Since: _______',
            'Medication: ___________________  Dose: _______  Since: _______',
            'Supplement: ___________________  Dose: _______  Since: _______',
            'Supplement: ___________________  Dose: _______  Since: _______',
        ]),
        ('QUESTIONS I WANT TO ASK', [
            '1. _____________________________________________________________',
            '2. _____________________________________________________________',
            '3. _____________________________________________________________',
            '4. _____________________________________________________________',
        ]),
    ]

    for title, lines in sections:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*SAGE_DARK)
        pdf.cell(0, 5, title, ln=True)
        pdf.ln(2)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*TEXT)
        for line in lines:
            pdf.cell(0, 7, line, ln=True)
            pdf.ln(1)
        pdf.ln(4)

    # Symptom summary box
    pdf.set_fill_color(*ROSE_LIGHT)
    pdf.rect(18, pdf.get_y(), 179.9, 36, 'F')
    pdf.set_xy(23, pdf.get_y() + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*ROSE)
    pdf.cell(0, 5, 'SYMPTOM SUMMARY (from your tracking data)')
    pdf.ln(7)
    summaries = [
        'Most frequent symptom: ________________________    Avg severity: ___/5',
        'Biggest identified trigger: _____________________',
        'Best symptom-free days were when I: __________________________________________',
        'Sleep average: _____ hours/night    Worst nights: ____________________________',
    ]
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*TEXT)
    for s in summaries:
        pdf.set_x(23)
        pdf.cell(0, 6, s, ln=True)

    pdf.ln(6)
    # Suggested questions
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*SAGE_DARK)
    pdf.cell(0, 5, 'QUESTIONS YOU MIGHT NOT THINK TO ASK:', ln=True)
    pdf.ln(2)

    questions = [
        "Should I get my hormone levels tested? If so, which ones and when in my cycle?",
        "Is HRT appropriate for me given my health history?",
        "Could my symptoms be related to thyroid function?",
        "What lifestyle changes would make the biggest difference for MY specific symptoms?",
        "Are there any supplements that are evidence-based for my main complaints?",
    ]
    for q in questions:
        pdf._checkbox_line(q, indent=0)

    pdf._page_footer_text()


def build_monthly_summary(pdf):
    """Monthly Patterns Summary."""
    pdf.add_page()
    pdf._brand_header_bar(SAGE)
    pdf.set_y(22)

    pdf._section_title('Monthly Patterns Summary')

    pdf._body_text(
        "After 4 weeks of tracking, fill in this summary page. This is your roadmap — "
        "it shows you exactly what's working and what isn't. Many women find this single "
        "page more valuable than the entire tracker."
    )
    pdf.ln(2)

    pdf._bold_text('Month: _______________     Year: _______', 10)
    pdf.ln(5)

    # Sections with fill lines
    fields = [
        ('TOP 3 SYMPTOMS THIS MONTH', 3),
        ('CONFIRMED TRIGGERS (things that made symptoms worse)', 3),
        ('CONFIRMED HELPERS (things that improved symptoms)', 3),
        ('PATTERNS I NOTICED', 4),
    ]

    for title, num_lines in fields:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*SAGE_DARK)
        pdf.cell(0, 5, title, ln=True)
        pdf.ln(2)
        pdf.set_draw_color(*SAGE_LIGHT)
        pdf.set_line_width(0.3)
        for i in range(num_lines):
            y = pdf.get_y()
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(*TEXT_MUTED)
            pdf.cell(5, 6, f'{i+1}.')
            pdf.line(25, y + 6, 197.9, y + 6)
            pdf.ln(8)
        pdf.ln(3)

    # Rating boxes
    pdf.set_fill_color(*CREAM)
    pdf.rect(18, pdf.get_y(), 179.9, 30, 'F')
    pdf.set_xy(23, pdf.get_y() + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*SAGE_DARK)
    pdf.cell(0, 5, 'MONTH-OVER-MONTH COMPARISON', ln=True)
    pdf.set_x(23)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*TEXT)
    pdf.ln(2)
    pdf.set_x(23)
    pdf.cell(0, 5, 'Overall symptom severity:    Much Worse  /  Worse  /  Same  /  Better  /  Much Better', ln=True)
    pdf.set_x(23)
    pdf.cell(0, 5, 'Sleep quality:                       Much Worse  /  Worse  /  Same  /  Better  /  Much Better', ln=True)
    pdf.set_x(23)
    pdf.cell(0, 5, 'Energy levels:                      Much Worse  /  Worse  /  Same  /  Better  /  Much Better', ln=True)

    pdf.ln(8)
    pdf._bold_text('GOALS FOR NEXT MONTH:', 9)
    pdf.ln(3)
    pdf.set_draw_color(*SAGE_LIGHT)
    for _ in range(3):
        y = pdf.get_y()
        pdf.line(18, y, 197.9, y)
        pdf.ln(8)

    pdf._page_footer_text()


def build_back_cover(pdf):
    """Final page: CTA to full planner."""
    pdf.add_page()
    # Full rose-light background
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, 0, 215.9, 279.4, 'F')

    # Top decorative bar
    pdf.set_fill_color(*SAGE)
    pdf.rect(0, 0, 215.9, 4, 'F')

    pdf.set_y(40)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*CHARCOAL)
    pdf.cell(0, 12, 'Enjoying This Tracker?', align='C', ln=True)

    pdf.ln(3)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(*TEXT)
    pdf.set_x(35)
    pdf.multi_cell(145.9, 6.5,
        "This free tracker is just one piece of the puzzle. "
        "The full Menopause Wellness Planner Bundle includes 34 pages of "
        "comprehensive tools designed to help you take complete control "
        "of your menopause journey.",
        align='C')

    pdf.ln(6)

    # Feature list
    features = [
        'Everything in this free tracker PLUS:',
        '34 beautifully designed printable pages',
        'Digital version for GoodNotes & Notability',
        'HRT tracking & medication schedules',
        'Comprehensive food & nutrition planner',
        'Exercise & movement tracker',
        'Mood journal with guided prompts',
        'Medical appointment organizer',
        'Monthly & quarterly review templates',
        'Goal setting & habit tracker worksheets',
    ]

    for i, f in enumerate(features):
        if i == 0:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(*SAGE_DARK)
            pdf.cell(0, 8, f, align='C', ln=True)
            pdf.ln(2)
        else:
            pdf.set_x(55)
            y = pdf.get_y()
            pdf.set_fill_color(*SAGE)
            pdf.ellipse(55, y + 1.5, 3, 3, 'F')
            pdf.set_x(62)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(*TEXT)
            pdf.cell(0, 6, f, ln=True)
            pdf.ln(1)

    pdf.ln(6)

    # CTA box
    pdf.set_fill_color(*SAGE)
    pdf.rect(35, pdf.get_y(), 145.9, 30, 'F')
    pdf.set_xy(35, pdf.get_y() + 5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(145.9, 8, 'Get the Full Planner Bundle', align='C', ln=True)
    pdf.set_x(35)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(145.9, 6, 'etsy.com/listing/4435219468', align='C', ln=True)

    # Bottom
    pdf.set_y(-40)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(0, 5, 'The Menopause Planner', align='C', ln=True)
    pdf.cell(0, 5, 'Real information. No fear. Just clarity.', align='C', ln=True)
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(0, 4, 'menopause-planner-website.vercel.app', align='C')


def main():
    pdf = TrackerPDF()
    pdf.set_title('Menopause Symptom Tracker — The Menopause Planner')
    pdf.set_author('The Menopause Planner')
    pdf.set_subject('Free menopause symptom tracking sheets')
    pdf.set_creator('The Menopause Planner')

    # Build all pages
    build_cover(pdf)             # 1
    build_welcome(pdf)           # 2
    build_baseline_assessment(pdf)  # 3
    build_weekly_tracker(pdf, 1) # 4
    build_weekly_tracker(pdf, 2) # 5
    build_weekly_tracker(pdf, 3) # 6
    build_weekly_tracker(pdf, 4) # 7
    build_food_trigger_log(pdf, 1)  # 8
    build_food_trigger_log(pdf, 2)  # 9
    build_sleep_tracker(pdf)     # 10
    build_doctor_prep(pdf)       # 11
    build_monthly_summary(pdf)   # 12
    build_back_cover(pdf)        # 13

    output_path = os.path.join(OUTPUT_DIR, 'menopause-symptom-tracker.pdf')
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Size: {size_kb:.0f} KB")


if __name__ == '__main__':
    main()
