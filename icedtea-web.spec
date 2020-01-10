# Version of java
%define javaver 1.8.0

# Alternatives priority
%define priority 18000
# jnlp prorocol gnome registry keys
%define gurlhandler   /desktop/gnome/url-handlers
%define jnlphandler   %{gurlhandler}/jnlp
%define jnlpshandler  %{gurlhandler}/jnlps

%define javadir     %{_jvmdir}/java-%{javaver}-openjdk
%define jredir      %{_jvmdir}/jre-%{javaver}-openjdk
%define javaplugin  libjavaplugin.so.%{_arch}

%define binsuffix      .itweb

%define preffered_java  java-%{javaver}-openjdk

Name:		icedtea-web
Version:	1.7.1
Release:	2%{?dist}
Summary:	Additional Java components for OpenJDK - Java browser plug-in and Web Start implementation

Group:      Applications/Internet
License:    LGPLv2+ and GPLv2 with exceptions
URL:        http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:    http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz
Patch0:     bashCompDirHardcodedAgain.patch
Patch1:     issue1.patch
Patch2:     issue2.patch
Patch3:     issue3.patch
Patch4:     PreventiveleQueue.patch
Patch11:    issue1-bin.patch
Patch33:    issue3-bin.patch

BuildRequires:  jpackage-utils
BuildRequires:  %{preffered_java}-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gecko-devel
BuildRequires:  glib2-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  xulrunner-devel
BuildRequires:  junit4
BuildRequires:  libappstream-glib
# new in 1.5 to have  clean up for malformed XMLs
BuildRequires:  tagsoup
# rhino is used as JS evaluator in testtime
BuildRequires:      rhino
# to apply binary tests for CVEs
BuildRequires:      git

# For functionality and the OpenJDK dirs
Requires:      %{preffered_java}
Requires:      jpackage-utils
Requires:      bash-completion
#maven fragments
Requires(post):      jpackage-utils
Requires(postun):      jpackage-utils

# For the mozilla plugin dir
Requires:       mozilla-filesystem%{?_isa}
# When itw builds against it, it have to be also in runtime
Requires:      tagsoup
# rhino is used as JS evaluator in runtime
Requires:      rhino

# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# jnlp protocols support
Requires(post):   GConf2
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7
# jnlp protocols support
Requires(postun):   GConf2

# Standard JPackage plugin provides.
Provides: java-plugin = 1:%{javaver}
Provides: javaws      = 1:%{javaver}

Provides:   %{preffered_java}-plugin =  1:%{version}
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


%package devel
Summary:    pure sources for debugging IcedTea-Web
Group:      devel
Requires:   %{name} = %{version}-%{release}
BuildArch:  noarch

%description devel
This package contains ziped sources of the IcedTea-Web project.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
if [ -e ../.git ] ; then
  mv ../.git ../ggit
fi
git apply --no-index --binary -v %{PATCH11}
git apply --no-index --binary -v %{PATCH33}
if [ -e ../ggit ] ; then
  mv ../ggit ../.git
fi

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

# icedteaweb-completion is currently not handled by make nor make install
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/policyeditor.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/javaws.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/itweb-settings.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/

# Move javaws man page to a more specific name
mv $RPM_BUILD_ROOT/%{_mandir}/man1/javaws.1 $RPM_BUILD_ROOT/%{_mandir}/man1/javaws.itweb.1

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications javaws.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications itweb-settings.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications policyeditor.desktop

# install MetaInfo file for firefox
mkdir -p %{buildroot}/%{_datadir}/appdata ; # just because appstream-util install do not work in rhel7
# broken in rhel7 DESTDIR=%{buildroot} appstream-util install metadata/%{name}.metainfo.xml
cp metadata/%{name}.metainfo.xml %{buildroot}/%{_datadir}/appdata/
# install MetaInfo file for javaws
# broken in rhel7 DESTDIR=%{buildroot} appstream-util install metadata/%{name}-javaws.appdata.xml
cp metadata/%{name}-javaws.appdata.xml %{buildroot}/%{_datadir}/appdata/

# maven fragments generation
mkdir -p $RPM_BUILD_ROOT%{_javadir}
pushd $RPM_BUILD_ROOT%{_javadir}
ln -s ../%{name}/netx.jar %{name}.jar
ln -s ../%{name}/plugin.jar %{name}-plugin.jar
popd
mkdir -p $RPM_BUILD_ROOT/%{_mavenpomdir}
cp  metadata/%{name}.pom  $RPM_BUILD_ROOT/%{_mavenpomdir}/%{name}.pom
cp metadata/%{name}-plugin.pom  $RPM_BUILD_ROOT/%{_mavenpomdir}/%{name}-plugin.pom

# __main__.IncompatibleFilenames: Filenames of POM /builddir/build/BUILDROOT/icedtea-web-1.6.2-1.el7.x86_64/usr/share/maven-poms/icedtea-web.pom and JAR /builddir/build/BUILDROOT/icedtea-web-1.6.2-1.el7.x86_64/usr/share/java/icedtea-web.jar does not match properly. Check that JAR subdirectories matches '.' in pom name.
# resolve before  7.2.z!
#add_maven_depmap %{name}.pom %{name}.jar
#add_maven_depmap %{name}-plugin.pom %{name}-plugin.jar

cp  netx.build/lib/src.zip  $RPM_BUILD_ROOT%{_datadir}/%{name}/netx.src.zip
cp liveconnect/lib/src.zip  $RPM_BUILD_ROOT%{_datadir}/%{name}/plugin.src.zip

%find_lang %{name} --all-name --with-man

%check
make check
appstream-util validate $RPM_BUILD_ROOT/%{_datadir}/appdata/*.xml || :

%post
alternatives \
  --install %{_libdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} %{_libdir}/IcedTeaPlugin.so %{priority}  --family %{preffered_java}.%{_arch} \
  --slave   %{_bindir}/javaws				javaws			%{_prefix}/bin/javaws%{binsuffix} \
  --slave   %{_bindir}/itweb-settings			itweb-settings		%{_prefix}/bin/itweb-settings%{binsuffix} \
  --slave   %{_bindir}/policyeditor			policyeditor		%{_prefix}/bin/policyeditor%{binsuffix} \
  --slave   %{_bindir}/ControlPanel			ControlPanel		%{_prefix}/bin/itweb-settings%{binsuffix} \
  --slave   %{_mandir}/man1/javaws.1.gz			javaws.1.gz		%{_mandir}/man1/javaws%{binsuffix}.1.gz \
  --slave   %{_mandir}/man1/ControlPanel.1.gz		ControlPanel.1.gz	%{_mandir}/man1/itweb-settings.1.gz


gconftool-2 -s  %{jnlphandler}/command  '%{_prefix}/bin/javaws%{binsuffix} %s' --type String &> /dev/null || :
gconftool-2 -s  %{jnlphandler}/enabled  --type Boolean true &> /dev/null || :
gconftool-2 -s %{jnlpshandler}/command '%{_prefix}/bin/javaws%{binsuffix} %s' --type String &> /dev/null || :
gconftool-2 -s %{jnlpshandler}/enabled --type Boolean true &> /dev/null || :

%posttrans
update-desktop-database &> /dev/null || :
exit 0

%postun
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ]
then
  alternatives --remove %{javaplugin} %{_libdir}/IcedTeaPlugin.so
  gconftool-2 -u  %{jnlphandler}/command &> /dev/null || :
  gconftool-2 -u  %{jnlphandler}/enabled &> /dev/null || :
  gconftool-2 -u %{jnlpshandler}/command &> /dev/null || :
  gconftool-2 -u %{jnlpshandler}/enabled &> /dev/null || :
fi
exit 0

# files -f .mfiles -f %{name}.lang
%files -f %{name}.lang
%defattr(-,root,root,-)
%{_sysconfdir}/bash_completion.d/*
%{_prefix}/bin/*
%{_libdir}/IcedTeaPlugin.so
%{_datadir}/applications/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.jar
%{_datadir}/%{name}/*.png
%{_datadir}/man/man1/*
%{_datadir}/pixmaps/*
%{_datadir}/appdata/*.xml
# thsoe four shouldnotbe there. Fixme! something went wrong
%{_mavenpomdir}/%{name}.pom
%{_mavenpomdir}/%{name}-plugin.pom
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-plugin.jar
%doc NEWS README
%license COPYING

%files javadoc
%defattr(-,root,root,-)
%{_datadir}/javadoc/%{name}
%license COPYING

%files devel
%{_datadir}/%{name}/*.zip
%license COPYING

%changelog
* Thu Jul 18 2019 Jiri Vanek <jvanek@redhat.com> 1.7.2-16
- added patch1, patch4 and patch11 to fix CVE-2019-10182
- added patch2 to fix CVE-2019-10181
- added patch3 and patch33 to fix CVE-2019-10185
- Resolves: rhbz#1724958 
- Resolves: rhbz#1725928 
- Resolves: rhbz#1724989 

* Mon Dec 18 2017 Jiri Vanek <jvanek@redhat.com> 1.7.1-1
* bump to 1.7.1
- Resolves: rhbz#1475411

* Fri Nov 03 2017 Jiri Vanek <jvanek@redhat.com> 1.7-3
- javaws specific manpage renmed from -suffix to .suffix
- Resolves: rhbz#1475411

* Wed Oct 18 2017 Jiri Vanek <jvanek@redhat.com> 1.7-2
- gathered various patches from usptream
- Resolves: rhbz#1475411

* Wed Oct 18 2017 Jiri Vanek <jvanek@redhat.com> 1.7-1
- updated to itw 1.7 and sync from fedora
- added forgotten slaves of itweb-settings policyeditor
- Own %%{_datadir}/%%{name} dir
- Mark non-English man pages with %%lang
- Install COPYING as %%license
- last three by Ville Skytta <ville.skytta@iki.fi> via 1481270
- for sake of rpms added patch0, bashCompDirHardcodedAgain.patch to hardcode bashcompletion dir
- removed maven macros in favour of manual handling (bug)
- Resolves: rhbz#1475411

* Thu Jul 14 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-4
- fixed typo in provides
- Resolves: rhbz#1299537

* Wed Jul 13 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-3
- added --family to make it part of javas alternatives alignment
- java-javaver-openjdk collected into preffered_java 
- Resolves: rhbz#1299537

* Wed Feb 03 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-1
- updated to 1.6.2
- fixed also rhbz#1303437 - package owns /etc/bash_completion.d but it should not own it 
- generated maven metadata (isntalled but not used. %add_maven_depmap need tobe fixed)
- Resolves: rhbz#1299537

* Wed Oct 14 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-4
- added and and applied patch2 fileLogInitializationError-1.6.patch to prevent 
consequences 1268909
- Resolves: rhbz#1217153

* Tue Sep 29 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-3
- added and applied patch1 donLogToFileBeforeFileLogsInitiate.patch
- Resolves: rhbz#1217153

* Mon Sep 21 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-2
- added and applied patch0 javadocFixes.patch 
- Resolves: rhbz#1217153

* Fri Sep 11 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-1
- updated to upstream release 1.6.1
- metadata xml files enhanced for javaws
- forced to use jdk8 by default
- Resolves: rhbz#1217153

* Thu Aug 27 2015 Jiri Vanek <jvanek@redhat.com> 1.6.0-2
- added gnome-software support
- Resolves: rhbz#1217153

* Thu Nov 27 2014 Jiri Vanek <jvanek@redhat.com> 1.6.0-1
- update to upstream 1.6
- made to use jdk8 (rh1184970)
- it will be necessary for 1.6.1 anyway (rh1233687)
- Resolves: rhbz#1217153

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
