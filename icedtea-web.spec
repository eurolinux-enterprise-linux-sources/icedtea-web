# Version of java
%define javaver 1.7.0

# Alternatives priority
%define priority 17000


%define javadir     %{_jvmdir}/java-openjdk
%define jredir      %{_jvmdir}/jre-openjdk
%define javaplugin  libjavaplugin.so.%{_arch}

%define binsuffix      .itweb

Name:		icedtea-web
Version:	1.5.2
Release:	0%{?dist}
Summary:	Additional Java components for OpenJDK - Java browser plug-in and Web Start implementation

Group:      Applications/Internet
License:    LGPLv2+ and GPLv2 with exceptions
URL:        http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:    http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz

BuildRequires:  java-%{javaver}-openjdk-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gecko-devel
BuildRequires:  glib2-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  xulrunner-devel
BuildRequires:  junit4
# new in 1.5 to have  clean up for malformed XMLs
BuildRequires:  tagsoup
# rhino is used as JS evaluator in testtime
BuildRequires:      rhino

# For functionality and the OpenJDK dirs
Requires:      java-%{javaver}-openjdk

# For the mozilla plugin dir
Requires:       mozilla-filesystem%{?_isa}

# When itw builds against it, it have to be also in runtime
Requires:      tagsoup

# rhino is used as JS evaluator in runtime
Requires:      rhino

# Post requires alternatives to install plugin alternative.
Requires(post):   %{_sbindir}/alternatives

# Postun requires alternatives to uninstall plugin alternative.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage plugin provides.
Provides: java-plugin = 1:%{javaver}
Provides: javaws      = 1:%{javaver}

Provides:   java-%{javaver}-openjdk-plugin =  1:%{version}
Obsoletes:  java-1.6.0-openjdk-plugin



%description
The IcedTea-Web project provides a Java web browser plugin, an implementation
of Java Web Start (originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations. 

%package javadoc
Summary:    API documentation for IcedTea-Web
Group:      Documentation
Requires:   %{name} = %{version}-%{release}
Requires:   jpackage-utils
BuildArch:  noarch

%description javadoc
This package contains Javadocs for the IcedTea-Web project.

%prep
%setup -q

%build
autoreconf -vfi
CXXFLAGS="$RPM_OPT_FLAGS $RPM_LD_FLAGS" \
%configure \
    --with-pkgversion=rhel-%{release}-%{_arch} \
    --docdir=%{_datadir}/javadoc/%{name} \
    --with-jdk-home=%{javadir} \
    --with-jre-home=%{jredir} \
    --libdir=%{_libdir} \
    --program-suffix=%{binsuffix} \
    --prefix=%{_prefix}
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Move javaws man page to a more specific name
mv $RPM_BUILD_ROOT/%{_mandir}/man1/javaws.1 $RPM_BUILD_ROOT/%{_mandir}/man1/javaws-itweb.1

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
cp javaws.png $RPM_BUILD_ROOT%{_datadir}/pixmaps
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications javaws.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications itweb-settings.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications policyeditor.desktop
ln -s  %{_mandir}/man1/javaws-itweb.1   $RPM_BUILD_ROOT/%{_mandir}/man1/icedtea-web.1

%check
make check

%post
alternatives \
  --install %{_libdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} \
  %{_libdir}/IcedTeaPlugin.so %{priority} \
  --slave %{_bindir}/javaws javaws %{_prefix}/bin/javaws%{binsuffix} \
  --slave %{_mandir}/man1/javaws.1.gz javaws.1.gz \
  %{_mandir}/man1/javaws-itweb.1.gz

%posttrans
update-desktop-database &> /dev/null || :

exit 0

%postun
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ]
then
  alternatives --remove %{javaplugin} \
    %{_libdir}/IcedTeaPlugin.so
fi

exit 0

%files
%defattr(-,root,root,-)
%{_prefix}/bin/*
%{_libdir}/IcedTeaPlugin.so
%{_datadir}/applications/*
%{_datadir}/icedtea-web
%{_datadir}/man/man1/*
%{_datadir}/pixmaps/*
%doc NEWS README COPYING

%files javadoc
%defattr(-,root,root,-)
%{_datadir}/javadoc/%{name}
%doc COPYING

%changelog
* Thu Nov 27 2014 Jiri Vanek <jvanek@redhat.com> 1.5.2-0
- update to upstream 1.5.2
- enabled tagsoup
- forced rhino
- Resolves: rhbz#1075793

* Fri Oct 17 2014 Jiri Vanek <jvanek@redhat.com> 1.5.1-3
- removed ExcludeArch: ppc
 - openjdk on ppc should be now fixed
- Resolves: rhbz#1075793

* Mon Aug 18 2014 Jiri Vanek <jvanek@redhat.com> 1.5.1-2
- added ExcludeArch: ppc
- Resolves: rhbz#1125557

* Mon Aug 18 2014 Jiri Vanek <jvanek@redhat.com> 1.5.1-1
- fixed obsolates to any jdk6 plugin
- Resolves: rhbz#1077287

* Fri Aug 15 2014 Jiri Vanek <jvanek@redhat.com> 1.5.1-0
- update to upstream 1.5.1
- removed all patches (all upstreamed)
- Resolves: rhbz#1077287

* Mon Apr 07 2014 Jiri Vanek <jvanek@redhat.com> 1.5-2
- add not yet upstreamed DE localisation of 1.5
 - patch0 DElocalizationforIcedTea-Web1.5-0001.patch
- autoreconf gog  -vfi, see RH1077898
- ./configure changed to %%configure
- Resolves: rhbz#1077287

* Tue Mar 11 2014 Jiri Vanek <jvanek@redhat.com> 1.4.2-1
- fixing brand in with-pkgversion switch to rhel
- Resolves: rhbz#1065518

* Mon Mar 10 2014 Jiri Vanek <jvanek@redhat.com> 1.4.2-0
- updated to 1.4.2
- Resolves: rhbz#1065518

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.4.1-2
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.4.1-1
- Mass rebuild 2013-12-27

* Tue Sep 24 2013 Jiri Vanek <jvanek@redhat.com> 1.4.1-0
- updated to 1.4.1
- add icedtea-web man page (resolves 948443)
- removed upstreamed  patch1 b25-appContextFix.patch
- removed upstreamed  patch2 rhino-pac-permissions.patch
- make check enabled again
- should be build for non-standart archs !-)
- removed unused multilib arches (yupii!)
- Resolves: rhbz#1009820

* Wed Jun 19 2013 Jiri Vanek <jvanek@redhat.com> 1.4.0-2
- added patch1 b25-appContextFix.patch to make it run with future openjdk

* Fri Jun 07 2013 Jiri Vanek <jvanek@redhat.com> 1.4-1
- Adapted to latest openjdk changes
- added build requires for autoconf and automake
- minor clean up

* Sat May 04 2013 Jiri Vanek <jvanek@redhat.com> 1.4-0
- Updated to 1.4
- See announcement for detail
 - http://mail.openjdk.java.net/pipermail/distro-pkg-dev/2013-May/023195.html
- commented out check - some junit4  incompatibility

* Wed Apr 17 2013 Jiri Vanek <jvanek@redhat.com> 1.3.2-0
- Updated to latest ustream release of 1.3 branch - 1.3.2
 - Security Updates
  - CVE-2013-1927, RH884705: fixed gifar vulnerability
  - CVE-2013-1926, RH916774: Class-loader incorrectly shared for applets with same relative-path.
 - Common
  - Added new option in itw-settings which allows users to set JVM arguments when plugin is initialized.
 - NetX
  - PR580: http://www.horaoficial.cl/ loads improperly
 - Plugin
   PR1260: IcedTea-Web should not rely on GTK
   PR1157: Applets can hang browser after fatal exception
- Removed upstreamed patch to remove GTK dependency
  - icedtea-web-pr1260-remove-gtk-dep.patch

* Wed Feb 20 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.3.1-5
- Resolves: rhbz#875496
- Build with $RPM_LD_FLAGS and %%{_smp_mflags}.
- Run unit tests during build.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Deepak Bhole <dbhole@redhat.com> 1.3.1-3
- Resolves: rhbz#889644, rhbz#895197
- Added patch to remove GTK dependency

* Thu Dec 20 2012 Jiri Vanek <jvanek@redhat.com> 1.3.1-2
- Moved to be  build with GTK3

* Wed Nov 07 2012 Deepak Bhole <dbhole@redhat.com> 1.3.1-1
- Resolves: RH869040/CVE-2012-4540

* Mon Sep 17 2012 Deepak Bhole <dbhole@redhat.com> 1.3-1
- Updated to 1.3
- Resolves: rhbz#720836: Epiphany fails to execute Java applets

* Tue Jul 31 2012 Deepak Bhole <dbhole@redhat.com> 1.2.1-1
- Updated to 1.2.1
- Resolves: RH840592/CVE-2012-3422
- Resolves: RH841345/CVE-2012-3423

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 03 2012 Deepak Bhole <dbhole@redhat.com> 1.2-4
- Resolves rhbz#814585
- Fixed java-plugin provides and added one for javaws

* Tue Apr 17 2012 Deepak Bhole <dbhole@redhat.com> 1.2-3
- Updated summary
- Fixed virtual provide

* Tue Mar 13 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.2-2
- Enable building on ARM platforms

* Mon Mar 05 2012 Deepak Bhole <dbhole@redhat.com> 1.2-1
- Updated to 1.2

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 25 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-3
- Resolves rhbz#757191
- Bumped min_openjdk_version to -60 (latest)

* Thu Nov 24 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-2
- Resolves: rhbz#742887. Do not own directories not created by the package.

* Tue Nov 08 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-1
- Updated to 1.1.4
- Added npapi-fix patch so that the plug-in compiles with xulrunner 8 

* Thu Sep 01 2011 Deepak Bhole <dbhole@redhat.com> 1.1.2-1
- Updated to 1.1.2
- Removed all patches (now upstream)
- Resolves: rhbz# 734890

* Tue Aug 23 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-3
- Added patch to allow install to jre dir
- Fixed requirement for java-1.7.0-openjdk

* Tue Aug 09 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-2
- Fixed file ownership so that debuginfo is not in main package

* Wed Aug 03 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-1
- Bump to 1.1.1
- Added patch for PR768 and PR769

* Wed Jul 20 2011 Deepak Bhole <dbhole@redhat.com> 1.0.4-1
- Bump to 1.0.4
- Fixed rhbz#718164: Home directory path disclosure to untrusted applications
- Fixed rhbz#718170: Java Web Start security warning dialog manipulation

* Mon Jun 13 2011 Deepak Bhole <dbhole@redhat.com> 1.0.3-1
- Update to 1.0.3
- Resolves: rhbz#691259 

* Mon Apr 04 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-2
- Fixed incorrect macro value for min_openjdk_version
- Use posttrans instead of post, so that upgrade from old plugin works

* Mon Apr 04 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-1
- Initial build
