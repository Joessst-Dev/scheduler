from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Team(models.Model):
    name = models.CharField('Name', max_length=255, blank=False)
    skill = models.IntegerField('Skill', validators=(MinValueValidator(1), MaxValueValidator(10)),
                                null=True, default=None)
    notes = models.TextField('Notes', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-name', '-skill']
        db_table = 'scheduler_team'


class Match(models.Model):
    title = models.CharField('Title', max_length=255, blank=False)
    opponent = models.ForeignKey(Team, on_delete=models.SET_NULL, verbose_name='Opponent', null=True)
    score_opponent = models.PositiveIntegerField('Score of the opponent', null=True, default=None)
    score = models.PositiveIntegerField('Our score', null=True, default=None)
    default_match_date = models.DateTimeField('Default match date')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-title']
        db_table = 'scheduler_match'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Find Appointment for that match
        has_appointment_instance = Appointment.objects.filter(match=self).exists()

        if has_appointment_instance is False:
            appointment = Appointment(match=self)
            appointment.save()


class Appointment(models.Model):
    match_date = models.DateTimeField('Match date', null=True, default=None)
    match = models.OneToOneField(Match, on_delete=models.CASCADE, verbose_name='Match', unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_date', '-match__default_match_date']
        db_table = 'scheduler_appointment'


class Proposition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField('Date')
    start_time = models.TimeField('Start time')
    end_time = models.TimeField('End time')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time', '-end_time']
        db_table = 'scheduler_proposition'

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start time can't be greater or equal to the end time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
