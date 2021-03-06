from datetime import datetime

from django_countries.fields import Country
from rest_framework import serializers
from contacts.models import Person
from contacts.serializers import PersonSerializer
from core.models import YesNoStatusChoice
from identity_verification.constants import VerificationSource
from identity_verification.models import (
    PersonVerification,
    Passport,
    PersonVerificationAttachment,
    DriverLicense,
    MedicareCard)
from identity_verification.trulioo import TruliooRequestBuilder
from identity_verification.utils import (
    is_passport_match,
    is_dvs_driver_license_match,
    is_dvs_medicare_card_match)


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = (
            'person',
            'number',
            'expiry_date',
            'place_of_birth',
            'country',
        )


class DriverLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriverLicense
        fields = (
            'person',
            'number',
            'state',
            'card_number',
            'expiry_date',
        )


class MedicareCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicareCard
        fields = (
            'person',
            'number',
            'reference_number',
            'expiry_date_year',
            'expiry_date_month',
            'colour',
        )


class IdentityVerificationSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField()
    verification_data = serializers.JSONField(required=False)
    person = serializers.JSONField()
    attachment_ids = serializers.ListField(required=False)

    class Meta:
        model = PersonVerification
        fields = (
            'type',
            'verification_data',
            'person',
            'attachment_ids'
        )

    def create(self, validated_data):
        submitted_person = validated_data['person']
        if submitted_person.get('id', None):
            person = Person.objects.get(pk=submitted_person['id'])
        else:
            person = PersonSerializer(data=submitted_person)
            person.is_valid()
            person = person.save()

        verification_type = validated_data['type']
        person_verification = PersonVerification.objects.create(
            person=person, source=verification_type, country=Country(code='AU')
        )

        if validated_data['type'] == VerificationSource.MANUAL_FILE_UPLOAD:
            # todo: handle file save, save it to PersonVerificationAttachment model
            person_verification.status = YesNoStatusChoice.PASSED
            for attachment_id in validated_data['attachment_ids']:
                pa = PersonVerificationAttachment.objects.get(pk=attachment_id)
                pa.verification=person_verification
                pa.save()

        if validated_data['type'] == VerificationSource.DVSPASSPORT:
            submitted_passport = validated_data['verification_data']['passport']
            submitted_passport.update({
                'person': person.pk,
                'country': Country(code=submitted_passport['country'])
            })
            passport = PassportSerializer(data=submitted_passport)
            passport.is_valid()
            passport.save()

            request_builder = TruliooRequestBuilder()
            request_builder.passport = passport
            request_builder.person = person

            raw_response = request_builder.request_verification([VerificationSource.DVSPASSPORT])
            if is_passport_match(raw_response):
                person_verification.status = YesNoStatusChoice.PASSED
            else:
                person_verification.status = YesNoStatusChoice.REJECTED
            person_verification.raw_response = raw_response
        elif validated_data['type'] == VerificationSource.DVSDRIVERLICENSE:
            submitted_driver_license = validated_data['verification_data']['driver_license']
            submitted_driver_license.update({'person': person.pk})
            serializer = DriverLicenseSerializer(data=submitted_driver_license)
            serializer.is_valid(raise_exception=True)
            driver_license = serializer.save()

            request_builder = TruliooRequestBuilder()
            request_builder.driver_license = driver_license
            request_builder.person = person
            raw_response = request_builder.request_verification([VerificationSource.DVSDRIVERLICENSE])
            if is_dvs_driver_license_match(raw_response):
                person_verification.status = YesNoStatusChoice.PASSED
            else:
                person_verification.status = YesNoStatusChoice.REJECTED
        elif validated_data['type'] == VerificationSource.DVSMEDICARECARD:
            submitted_medicare_card = validated_data['verification_data']['medicare_card']
            submitted_medicare_card.update({'person': person.pk})
            serializer = MedicareCardSerializer(data=submitted_medicare_card)
            serializer.is_valid(raise_exception=True)
            medicare_card = serializer.save()

            request_builder = TruliooRequestBuilder()
            request_builder.medicare_card = medicare_card
            request_builder.person = person
            raw_response = request_builder.request_verification([VerificationSource.DVSMEDICARECARD])
            from pprint import pprint
            pprint(raw_response)
            if is_dvs_medicare_card_match(raw_response):
                person_verification.status = YesNoStatusChoice.PASSED
            else:
                person_verification.status = YesNoStatusChoice.REJECTED
        person_verification.save()
        return person_verification


class PersonVerificationAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonVerificationAttachment
        fields = (
            'id',
            'file',
            'verification',
        )
        extra_kwargs = {
            'file': {'write_only': True},
            'verification': {'write_only': True}
        }
