
%define multilib_arches ppc64 sparc64 x86_64

# Version of java
%define javaver 1.7.0

# Alternatives priority
%define priority        16000

%ifarch %{ix86}
%define archbuild i586
%define archinstall i386
%endif
%ifarch x86_64
%define archbuild amd64
%define archinstall amd64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%define archbuild sparc
%define archinstall sparc
%endif
# 64 bit sparc
%ifarch sparc64
%define archbuild sparcv9
%define archinstall sparcv9
%endif

%ifarch %{multilib_arches}
%define javadir        %{_jvmdir}/java-%{javaver}-openjdk.%{_arch}
%define jredir         %{_jvmdir}/jre-%{javaver}-openjdk.%{_arch}
%define jre6dir         %{_jvmdir}/jre-1.6.0-openjdk.%{_arch}
%define javaplugin     libjavaplugin.so.%{_arch}
%else
%define javadir        %{_jvmdir}/java-%{javaver}-openjdk
%define jredir         %{_jvmdir}/jre-%{javaver}-openjdk
%define jre6dir         %{_jvmdir}/jre-1.6.0-openjdk
%define javaplugin      libjavaplugin.so
%endif

%define binsuffix      .itweb

Name:		icedtea-web
Version:	1.2.3
Release:	4%{?dist}
Summary:	Additional Java components for OpenJDK

Group:		Applications/Internet
License:	LGPLv2+ and GPLv2 with exceptions
URL:		http://icedtea.classpath.org/wiki/IcedTea-Web

# hg clone http://icedtea.classpath.org/hg/release/icedtea-web-1.2 -r c959afd1eba7
Source0:	http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz

Patch1:		b25-appContextFix.patch


BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  java-%{javaver}-openjdk-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gecko-devel
BuildRequires:  glib2-devel
BuildRequires:  gtk2-devel
BuildRequires:  xulrunner-devel

# For functionality and the OpenJDK dirs
Requires:	    java-%{javaver}-openjdk

# For the mozilla plugin dir
Requires:       mozilla-filesystem%{?_isa}

# Post requires alternatives to install plugin alternative.
Requires(post):   %{_sbindir}/alternatives

# Postun requires alternatives to uninstall plugin alternative.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage plugin provides.
Provides: java-plugin = 1:%{javaver}
Provides: javaws      = 1:%{javaver}

Provides:   java-%{javaver}-openjdk-plugin =  1:%{version}
Obsoletes:  java-1.6.0-openjdk-plugin

ExclusiveArch: x86_64 i686

%description
The IcedTea-Web project provides a Java web browser plugin, an implementation
of Java Web Start (originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations. 

%package javadoc
Summary:    API documentation for IcedTea-Web
Group:      Documentation
Requires:   %{name} = %{version}-%{release}

%description javadoc
This package contains Javadocs for the IcedTea-Web project.

%prep
%setup -q

%patch1 -p1

%build
./configure \
    --with-pkgversion=rhel-%{release}-%{_arch} \
    --docdir=%{_datadir}/javadoc/%{name} \
    --with-jdk-home=%{javadir} \
    --with-jre-home=%{jredir} \
    --libdir=%{_libdir} \
    --program-suffix=%{binsuffix} \
    --prefix=%{_prefix}

make

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

# Link to .so file from JRE_HOME as plug-in is bound to a specific version
install -dm 755 $RPM_BUILD_ROOT%{jredir}/lib/%{archinstall}/
ln -s %{_libdir}/IcedTeaPlugin.so \
	$RPM_BUILD_ROOT%{jredir}/lib/%{archinstall}/IcedTeaPlugin.so

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-desktop-database &> /dev/null || :
MAKE_THIS_DEFAULT=0
if [ $1 -gt 1 ] # update
then

# Is the previous one set as a maual alternative?
alternatives --display %{javaplugin} | head -n 1 | grep -q "status is auto"
if [ $? -ne 0 ]; then # If not 1, it is manual
  alternatives --display %{javaplugin} | grep "link currently points to" | grep -q "%{jre6dir}/lib/%{archinstall}/IcedTeaPlugin.so$"
  if [ $? -eq 0 ]; then
    MAKE_THIS_DEFAULT=1
  fi
fi

alternatives --remove %{javaplugin} \
  %{jre6dir}/lib/%{archinstall}/IcedTeaPlugin.so 2>/dev/null  	

fi
alternatives \
  --install %{_libdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} \
  %{jredir}/lib/%{archinstall}/IcedTeaPlugin.so %{priority} \
  --slave %{_bindir}/javaws javaws %{_prefix}/bin/javaws%{binsuffix} \
  --slave %{_mandir}/man1/javaws.1.gz javaws.1.gz \
  %{_mandir}/man1/javaws-itweb.1.gz


# Gracefully update to this one if needed
if [ $MAKE_THIS_DEFAULT -eq 1 ]; then
alternatives --set %{javaplugin} %{jredir}/lib/%{archinstall}/IcedTeaPlugin.so
fi

exit 0

%postun
if [ $1 -eq 0 ]
  then
    update-desktop-database &> /dev/null || :
    alternatives --remove %{javaplugin} \
      %{jredir}/lib/%{archinstall}/IcedTeaPlugin.so
 fi
exit 0


%files
%defattr(-,root,root,-)
%{jredir}/lib/%{archinstall}/*
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

%changelog
* Wed Jun 19 2013 Jiri Vanek <jvanek@redhat.com> 1.2.3-4
- improved patch1 b25-appContextFix.patch to make it run with future openjdk better
- Resolves: rhbz#975426

* Tue Jun 18 2013 Jiri Vanek <jvanek@redhat.com> 1.2.3-3
- added patch1 b25-appContextFix.patch to make it run with future openjdk
- rmeoved posttrans
- Resolves: rhbz#975426

* Fri Apr 12 2013 Jiri Vanek <jvanek@redhat.com> 1.2.3-2
- Added (temporally!) posttrans forcing creation of symlinks
  - should be removed next release
- Resolves: rhbz#949094

* Fri Apr 12 2013 Jiri Vanek <jvanek@redhat.com> 1.2.3-1
- fixed postun - removal of alternatives for plugin restricted to 
  (correct) removal process only
- fixed date in changelog previous entry
- Resolves: rhbz#949094

* Thu Apr 11 2013 Jiri Vanek <jvanek@redhat.com> 1.2.3-0
- Updated to latest ustream release of 1.2 branch - 1.2.3
 - Security Updates
  - CVE-2013-1927, RH884705 - fixed gifar vulnerability
  - CVE-2013-1926, RH916774: Class-loader incorrectly shared for applets with same relative-path.
 - Common
  - PR1161: X509VariableTrustManager does not work correctly with OpenJDK7
 - Plugin
  - PR1157: Applets can hang browser after fatal exception
- Removed upstreamed patch 0- icedtea-web-PR1161.patch
- Resolves: rhbz#949094

* Fri Dec 07 2012 Jiri Vanek <jvanek@redhat.com> 1.2.2-3
- Fixed provides and obsolates
- Resolves: rhbz#838084.

* Mon Dec 03 2012 Deepak Bhole <dbhole@redhat.com> 1.2.2-2
- Build with OpenJDK7
- Import fix for PR1161 (needed for proper functionality with OpenJDK7)

* Thu Nov 01 2012 Deepak Bhole <dbhole@redhat.com> 1.2.2-1
- Updated to 1.2.2
- Resolves: CVE-2012-4540

* Wed Jul 25 2012 Deepak Bhole <dbhole@redhat.com> 1.2.1-1
- Updated to 1.2.1
- Resolves: CVE-2012-3422
- Resolves: CVE-2012-3423

* Mon Mar 05 2012 Deepak Bhole <dbhole@redhat.com> 1.2-1
- Updated to 1.2 proper

* Wed Feb 15 2012 Deepak Bhole <dbhole@redhat.com> 1.2-0.1.2pre
- Updated to 1.2pre snapshot

* Fri Oct 28 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-1
- Updated to 1.1.4
- Resolves: rhbz#744739

* Tue Oct 11 2011 Deepak Bhole <dbhole@redhat.com> 1.1.3-1
- Bumped to 1.1.3
- Fixed alternative removal command
- Resolves: rhbz#741796

* Tue Sep 20 2011 Deepak Bhole <dbhole@redhat.com> 1.1.2-2
- Resolves: rhbz#737899. Do not own directories not created by the package.

* Wed Aug 31 2011 Deepak Bhole <dbhole@redhat.com> 1.1.2-1
- Updated to 1.1.2
- Resolves: rhbz#683479
- Resolves: rhbz#725794
- Resolves: rhbz#718181 
- Resolves: rhbz#731358
- Resolves: rhbz#725718
- Use the new --with-jre-home switch (#731358)

* Mon Jul 25 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-1
- Bump to 1.1.1
- Removed icedtea-web-shared-classloader.patch (now upstream)
- Updated alternative removal commands to reflect the situation in RHEL6
- Resolves: rhbz#713514

* Tue Apr 05 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-3
- Added update-desktop-database directives in post and postun 

* Tue Apr 05 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-2
- Resolves rhbz#693601
- Added epochs to java plugin and javaws provides to match those of Oracle

* Tue Apr 05 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-1
- Resolves rhbz#693601 
- Update to IcedTea-Web 1.0.2
- Dropped patch0 (instance validity check). Now part of 1.0.2
- Also resolves #682674 by adding a javaws Provides

* Mon Mar 28 2011 Deepak Bhole <dbhole@redhat.com> 1.0.1-4
- Removed icedtea-web-desktop-encoding.patch which now causes rpmlint warnings 

* Mon Mar 28 2011 Deepak Bhole <dbhole@redhat.com> - 1.0.1-3
- Resolves rhbz#645781 (desktop sharing now works)
- Updated the classloader sharing patch to fix loader sharing rules
- Added version and release string in plugin display

* Fri Mar 04 2011 Deepak Bhole <dbhole@redhat.com> - 1.0.1-2
- Resolved rhbz#645781: MS Live Meeting Applet Not Working With OpenJDK Plugin

* Tue Feb 22 2011 Deepak Bhole <dbhole@redhat.com> - 1.0.1-1
- Bumped to 1.0.1
- Removed icedtea-web-pkg-access.patch (now upstream)
- Resolves CVE-2011-0706 and CVE-2010-4450

* Wed Feb 09 2011 Deepak Bhole <dbhole@redhat.com> - 1.0-5
- Minor comment/group/etc. updates from omajid@redhat.com
- Added base package requirement for javadoc subpackage

* Fri Feb 04 2011 Deepak Bhole <dbhole@redhat.com> - 1.0-4
- Added encoding to desktop files

* Wed Feb 02 2011 Deepak Bhole <dbhole@redhat.com> - 1.0-3
- Bump to 1.0 proper
- Install to jre dir only
- Restrict access to net.sourceforge.jnlp.*
- Resolves bugs 674519, 674517, 674524, 671470

* Fri Jan 14 2011 Deepak Bhole <dbhole@redhat.com> - 1.0-2
- Made exclusive arch
- Fixed archinstall macro value
- Fixed min required OpenJDK version to match what is in RHEL6
- Added BR for desktop-file-utils

* Fri Jan 14 2011 Deepak Bhole <dbhole@redhat.com> - 1.0-1
- Initial build with 1.0pre
