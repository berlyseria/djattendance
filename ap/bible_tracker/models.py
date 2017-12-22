from django.db import models
from django.contrib.postgres.fields import HStoreField
from accounts.models import Trainee
# from verse_parse.bible_re import *

import json

class BibleReading(models.Model):
  trainee = models.ForeignKey(Trainee, null=True)
  weekly_reading_status = HStoreField()
  books_read = HStoreField()

  # Default for First-year and Second-year bible reading
  # bible_books = testaments['ot'] + testaments['nt']
  # bible_books_list = [book[0] for book in bible_books]
  
  def weekly_statistics(self, start_week, end_week, term_id):
    trainee_stats = {'firstname': self.trainee.firstname, 'lastname': self.trainee.lastname, 'current_term': self.trainee.current_term}

    number_complete = 0
    number_madeup = 0
    number_notread = 0
    number_blank = 0
    number_complete_madeup = 0
    number_days = float((end_week - start_week +1) *7)

    for week in range(start_week, end_week + 1):
      term_week_id = str(term_id) + "_" + str(week)
      if term_week_id in self.weekly_reading_status:
        trainee_weekly_reading = self.weekly_reading_status[term_week_id]
        json_weekly_reading = json.loads(trainee_weekly_reading)
        weekly_status = json_weekly_reading['status']
        # Counts number of days in week with (C)omplete, (M)adeup, (_)Blank , and (C+M)Complete + Madeup
        number_complete += weekly_status.count('C')
        number_madeup += weekly_status.count('M')
        number_notread += weekly_status.count('N')
        number_blank += weekly_status.count('_')
        number_complete_madeup += (weekly_status.count('C') + weekly_status.count('M'))

    # Calculates percentages and adds to stats dictionary, along with final counts
    trainee_stats['number_complete'] = number_complete
    trainee_stats['percent_complete'] = int((number_complete/number_days) *100)
    trainee_stats['number_madeup'] = number_madeup
    trainee_stats['percent_madeup'] = int((number_madeup/number_days) * 100)
    trainee_stats['number_notread'] = number_notread
    trainee_stats['percent_notread'] = int((number_notread/number_days) *100)
    trainee_stats['number_blank'] = number_blank
    trainee_stats['percent_blank'] = int((number_blank/number_days) * 100)
    trainee_stats['number_complete_madeup'] = number_complete_madeup
    trainee_stats['percent_complete_madeup'] = int((number_complete_madeup/number_days) *100)
    trainee_stats['number_filled'] = trainee_stats['number_complete_madeup'] + trainee_stats['number_notread']

    return trainee_stats

  def calcFirstYearProgress(self):
    user_checked_list = self.books_read
    first_year_checked_list = [int(book_code.split("_")[1]) for book_code in user_checked_list.keys() if book_code.startswith('1_')]
    first_year_progress = 0

    for checked_book in first_year_checked_list:
      first_year_progress = first_year_progress + sum([int(chapter_verse_count) for chapter_verse_count in bible_books[checked_book][3]])

    return (first_year_checked_list, int(float(first_year_progress) / 31102.0 * 100))

  def calcSecondYearProgress(self):
    user_checked_list = self.books_read
    second_year_checked_list = [int(book_code.split("_")[1]) for book_code in user_checked_list.keys() if book_code.startswith('2_')]
    second_year_progress = 0

    for checked_book in second_year_checked_list:
      second_year_progress = second_year_progress + sum([int(chapter_verse_count) for chapter_verse_count in bible_books[checked_book][3]])

    return (second_year_checked_list, int(float(second_year_progress) / 7957.0 * 100))