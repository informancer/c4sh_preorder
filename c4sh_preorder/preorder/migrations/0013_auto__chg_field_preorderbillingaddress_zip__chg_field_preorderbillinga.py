# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PreorderBillingAddress.zip'
        db.alter_column(u'preorder_preorderbillingaddress', 'zip', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'PreorderBillingAddress.firstname'
        db.alter_column(u'preorder_preorderbillingaddress', 'firstname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'PreorderBillingAddress.city'
        db.alter_column(u'preorder_preorderbillingaddress', 'city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'PreorderBillingAddress.address1'
        db.alter_column(u'preorder_preorderbillingaddress', 'address1', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'PreorderBillingAddress.lastname'
        db.alter_column(u'preorder_preorderbillingaddress', 'lastname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'PreorderBillingAddress.country'
        db.alter_column(u'preorder_preorderbillingaddress', 'country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'PreorderBillingAddress.zip'
        db.alter_column(u'preorder_preorderbillingaddress', 'zip', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

        # Changing field 'PreorderBillingAddress.firstname'
        db.alter_column(u'preorder_preorderbillingaddress', 'firstname', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

        # Changing field 'PreorderBillingAddress.city'
        db.alter_column(u'preorder_preorderbillingaddress', 'city', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

        # Changing field 'PreorderBillingAddress.address1'
        db.alter_column(u'preorder_preorderbillingaddress', 'address1', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

        # Changing field 'PreorderBillingAddress.lastname'
        db.alter_column(u'preorder_preorderbillingaddress', 'lastname', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

        # Changing field 'PreorderBillingAddress.country'
        db.alter_column(u'preorder_preorderbillingaddress', 'country', self.gf('django.db.models.fields.CharField')(default='not specified', max_length=255))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'preorder.custompreorder': {
            'Meta': {'object_name': 'CustomPreorder', '_ormbases': [u'preorder.Preorder']},
            u'preorder_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['preorder.Preorder']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'preorder.custompreorderticket': {
            'Meta': {'ordering': "['sortorder']", 'object_name': 'CustomPreorderTicket', '_ormbases': [u'preorder.PreorderTicket']},
            u'preorderticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['preorder.PreorderTicket']", 'unique': 'True', 'primary_key': 'True'}),
            'sortorder': ('django.db.models.fields.IntegerField', [], {})
        },
        u'preorder.goldentoken': {
            'Meta': {'object_name': 'GoldenToken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redeem_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'redeemed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redeemer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.PreorderTicket']"}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'preorder.merchandise': {
            'Meta': {'object_name': 'Merchandise'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'detail_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'detail_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'preview_image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'preorder.preorder': {
            'Meta': {'object_name': 'Preorder'},
            'additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cached_sum': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'paid_via': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'unique_secret': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'preorder.preorderbillingaddress': {
            'Meta': {'object_name': 'PreorderBillingAddress'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'preorder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.CustomPreorder']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'preorder.preorderposition': {
            'Meta': {'object_name': 'PreorderPosition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preorder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.Preorder']"}),
            'redeemed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.PreorderTicket']"}),
            'uuid': ('c4sh.preorder.models.UUIDField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'})
        },
        u'preorder.preorderquota': {
            'Meta': {'object_name': 'PreorderQuota'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['preorder.PreorderPosition']", 'null': 'True', 'blank': 'True'}),
            'quota': ('django.db.models.fields.IntegerField', [], {}),
            'sold': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.CustomPreorderTicket']"})
        },
        u'preorder.preorderticket': {
            'Meta': {'ordering': "['active', 'name', '-price']", 'object_name': 'PreorderTicket'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backend_id': ('django.db.models.fields.SmallIntegerField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ticket': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'limit_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'limit_amount_user': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'limit_timespan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'tax_rate': ('django.db.models.fields.SmallIntegerField', [], {'default': '19'}),
            'valid_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'preorder.tshirt': {
            'Meta': {'ordering': "['sortorder']", 'object_name': 'Tshirt', '_ormbases': [u'preorder.CustomPreorderTicket']},
            u'custompreorderticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['preorder.CustomPreorderTicket']", 'unique': 'True', 'primary_key': 'True'}),
            'merchandise': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['preorder.Merchandise']"}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'preorder.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'user_profile'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['preorder']