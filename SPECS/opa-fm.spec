# One of the steps this package's insane build system does is patching version
# strings in built binaries (MakeTools/patch_version/patch_version.c).
# The expected template of a version string (ICS_BUILD_VERSION from
# CodeVersion/code_version.c) is not found in binaries that contain a
# GetCodeVersion() call. I suspect LTO optimizes it away.
# Disabling LTO made the build work.
%global _lto_cflags %{nil}

Name: opa-fm
Epoch: 1
Version: 10.12.1.0.6
Release: 1%{?dist}
Summary: Intel Omni-Path Fabric Management Software

License: GPLv2 or BSD
Url: https://github.com/cornelisnetworks/opa-fm
Source0: https://github.com/cornelisnetworks/opa-fm/archive/refs/tags/v%{version}.tar.gz

# bz1262327 needs Patch0002
Patch0002: 0001-Fix-well-known-tempfile-issue-in-script.patch
Patch0003: opafm-link-all-executables-with-pie.patch
Patch0004: add-fPIC-flag.patch

BuildRequires: openssl-devel, expat-devel
BuildRequires: libibverbs-devel >= 1.2.0
BuildRequires: libibumad-devel
BuildRequires: zlib-devel
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: systemd-rpm-macros
Requires: libhfi1
ExclusiveArch: x86_64

%description
opa-fm contains Intel Omni-Path fabric management applications. This
includes: the Subnet Manager, Baseboard Manager, Performance Manager,
Fabric Executive, and some fabric management tools.

%prep
%setup -q
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1

# Make it possible to override hardcoded compiler flags
sed -i -r -e 's/(release_C(C)?OPT_Flags\s*)=/\1?=/' Makerules/Target.LINUX.GNU.*
sed -r -e 's/(^COPT\s*=\s*)/#\1/' -i Esm/ib/src/linux/opafmvf/Makefile

%build
export CFLAGS='%{optflags} -std=gnu11'
export CXXFLAGS='%{optflags} -std=gnu11'
export release_COPT_Flags='%{optflags} -std=gnu11'
export release_CCOPT_Flags='%{optflags} -std=gnu11'
cd Esm
OPA_FEATURE_SET=opa10 ./fmbuild $BUILD_ARGS

%install
BUILDDIR=%{_builddir} DESTDIR=%{buildroot} LIBDIR=%{_libdir} RPM_INS=n ./Esm/fm_install.sh
chmod 644 %{buildroot}/%{_unitdir}/opafm.service
mkdir -p %{buildroot}/%{_localstatedir}/usr/lib/opa-fm/
chmod a-x %{buildroot}/%{_prefix}/share/opa-fm/opafm_src.xml

%post
%systemd_post opafm.service

%preun
%systemd_preun opafm.service

%postun
%systemd_postun_with_restart opafm.service

%files
%doc Esm/README
%{_unitdir}/opafm.service
%config(noreplace) %{_sysconfdir}/opa-fm/opafm.xml
%config(noreplace) %{_sysconfdir}/opa-fm/opafm_pp.xml
%{_sysconfdir}/opa-fm
%{_prefix}/lib/opa-fm/bin/*
%{_prefix}/lib/opa-fm/runtime/*
%{_prefix}/share/opa-fm/*
%{_sbindir}/opafmcmd
%{_sbindir}/opafmcmdall
%{_sbindir}/opafmconfigpp
%{_sbindir}/opafmvf
%{_mandir}/man8/*

%changelog
* Fri Jun 02 2023 Kamal Heib <kheib@redhat.com> - 1:10.12.1.0.6-1
- Update to upstream release 10.12.1.0.6
- Resolves: rhbz#2170632, rhbz#2159649

* Thu Feb 02 2023 Michal Schmidt <mschmidt@redhat.com> - 10.11.2.0.3-1
- Update to upstream release 10.11.2.0.3
- Resolves: rhbz#2111129

* Wed Aug 03 2022 Michal Schmidt <mschmidt@redhat.com> - 10.11.1.3.1-1
- Update to upstream release 10.11.1.3.1
- Resolves: rhbz#2049171

* Tue Oct 19 2021 Honggang Li <honli@redhat.com> - 1:10.11.0.2-1
- Rebase to upstream release 10.11.0.2
- Resolves: rhbz2013070

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1:10.11.0.1.2-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 1:10.11.0.1.2-2
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Wed Apr 28 2021 Honggang Li <honli@redhat.com> - 10.11.0.1.2-1
- Rebase to upstream release 10.11.0.1.2
- Resolves: rhbz1924901
