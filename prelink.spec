Summary:	Tool to optimize relocations in object files
Name:		prelink
Version:	20111012
Release:	4
License:	GPL
Group:		Development/Tools
Source0:	http://people.redhat.com/jakub/prelink/%{name}-%{version}.tar.bz2
# Source0-md5:	f5aaf347432d677c293e5e3399ba4fdf
Source1:	%{name}.conf
Source2:	%{name}.cron
Source3:	%{name}.sysconfig
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	elfutils-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
Requires(post):	coreutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This program replaces relocations in object files with less expensive
ones. This allows faster run-time dynamic linking.

%prep
%setup -qn %{name}

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	ac_cv_lib_selinux_is_selinux_enabled=no	\
	--enable-static=no
%{__make}

%if 0
%check
%{__make} -C testsuite check-harder
%{__make} -C testsuite check-cycle
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{sysconfig,rpm,cron.daily}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.daily/prelink
cp -a %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/prelink

install -d $RPM_BUILD_ROOT/var/{lib/misc,log}
touch $RPM_BUILD_ROOT/var/lib/misc/prelink.full
touch $RPM_BUILD_ROOT/var/lib/misc/prelink.quick
touch $RPM_BUILD_ROOT/var/lib/misc/prelink.force
touch $RPM_BUILD_ROOT/var/log/prelink.log

cat > $RPM_BUILD_ROOT/etc/rpm/macros.prelink <<'EOF'
# rpm-4.1 verifies prelinked libraries using a prelink undo helper.
#       Note: The 2nd token is used as argv[0] and "library" is a
#       placeholder that will be deleted and replaced with the appropriate
#       library file path.
%%__prelink_undo_cmd %{_sbindir}/prelink prelink -y library
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
umask 002
touch /var/lib/misc/prelink.force

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README THANKS TODO
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/prelink.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/prelink
/etc/rpm/macros.prelink
%attr(755,root,root) /etc/cron.daily/prelink
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man?/*
%verify(not md5 mtime size) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.full
%verify(not md5 mtime size) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.quick
%verify(not md5 mtime size) %ghost %config(missingok,noreplace) /var/lib/misc/prelink.force
%verify(not md5 mtime size) %ghost %config(missingok,noreplace) /var/log/prelink.log

