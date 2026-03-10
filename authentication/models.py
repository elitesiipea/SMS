from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# BaseUserManager Model Manager

class MyUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

# UserManager Model Manager


class User(AbstractBaseUser, PermissionsMixin):

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True, null=True)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="user_etablissement", on_delete=models.CASCADE, null=True, blank=True)
    is_staff = models.BooleanField(
         _("AUTORISER AU SITE"),
        default=False,
        help_text=_('Indique si l"utilisateur peut se connecter à ce site.'),
    )
    is_super_admin = models.BooleanField(
        _("SUPER ADMINISTRATEUR"),
        default=False,
        help_text=_('Indique si l"utilisateur est super administrateur .'),
    )

    is_medecin = models.BooleanField(
        _("MEDECIN"),
        default=False,
        help_text=_('Indique si l"utilisateur peut accéder aux données médicales'),
    )

    is_stock = models.BooleanField(
        _("GESTION DES KITS ET ACCESSOIRES"),
        default=False,
        help_text=_('Indique si l"utilisateur gère la remise de kits & accessoires'),
    )

    can_view_stock = models.BooleanField(
        _("VOIR HISTORIQUE DES KITS ET ACCESSOIRES"),
        default=False,
        help_text=_("Indique si l'utilisateur voit l'historique des kits & accessoires"),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_(
            'Indique si cet utilisateur doit être traité comme actif. '
            "Désélectionner ceci au lieu de supprimer des comptes."
        ),
    )

    is_student = models.BooleanField(
        _('ÉTUDIANT'),
        default=False,
        help_text=_('Cocher si l"utilisateur est un étudiant.'),
    )

    is_teacher = models.BooleanField(
        _('ENSEIGNANT'),
        default=False,
        help_text=_('Cocher si l"utilisateur est un enseignant.'),
    )


    can_register_student = models.BooleanField(
        _('AUTORISER À INSCRIRE DES ÉTUDIANTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut inscrire des Étudiants.'),
    )

    can_register_teacher = models.BooleanField(
        _('AUTORISER À INSCRIRE DES ENSEIGNANTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut inscrire des Enseignants.'),
    )

    can_view_teacher_profile_and_contrat = models.BooleanField(
        _('AUTORISER À VOIR LE PROFIL ET LE CONTRAT DES ENSEIGNANTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut voir le profil et le contrat des enseignants.'),
    )

    can_view_teacher_acccompte = models.BooleanField(
        _('AUTORISER À VOIR LES DEMANDES D\'ACCOMPTE DES ENSEIGNANTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut voir les demandes d\'acompte des enseignants.'),
    )

    can_manage_teacher_acccompte = models.BooleanField(
        _('AUTORISER À GÉRER LES ACCOMPTES DES ENSEIGNANTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut gérer les comptes des enseignants.'),
    )

    can_manage_fees = models.BooleanField(
        _('AUTORISER À VOIR LES SCOLARITÉS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut voir les scolarités.'),
    )

    can_update_fees = models.BooleanField(
        _('AUTORISER À METTRE À JOUR LES SCOLARITÉS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut mettre à jour les scolarités.'),
    )
    
    is_transport = models.BooleanField(
        _('AUTORISER GERER LES TRANSPORTS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut gerer les transport.'),
    )

    can_add_note = models.BooleanField(
        _('AUTORISER À AJOUTER DES NOTES'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut ajouter des notes.'),
    )

    can_update_time = models.BooleanField(
        _('AUTORISER À MODIFIER LES EMPLOIS DU TEMPS'),
        default=False,
        help_text=_('Cocher si l"utilisateur peut modifier les emplois du temps.'),
    )

    can_view_index_summary = models.BooleanField(
        _("AUTORISER À VOIR LE SOMMAIRE DES DONNÉES SUR L'INDEX"),
        default=False,
        help_text=_('Cocher si l"utilisateur est autorisé à voir le sommaire des données sur l\'index.'),
    )

    can_make_emargement = models.BooleanField(
        _("AUTORISER À EFFECTUER LES EMARGEMENTS"),
        default=False,
        help_text=_('Cocher si l"utilisateur est faire les émargements.'),
    )

    can_manage_diplome = models.BooleanField(
    _("AUTORISER À GERER LES DIPLOMES ET CERTIFICATS"),
    default=False,
    help_text=_('Cocher si l"utilisateur autorisé À GERER LES DIPLOMES ET CERTIFICATS.'),
    )
    
    overloader = models.BooleanField(
        _('OVERLOADER'),
        default=False,
        help_text=_('Ne pas Cocher OVERLOADER'),
    )
    

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return "{} {}".format(self.nom, self.prenom)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email